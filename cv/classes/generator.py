import os
import jsonpickle
from cv.classes import config as cp
from settings import resources as r
from recordclass import recordclass
from settings.timeit import timeit
from cv.classes.game_events import *
from cv.classes.gamestate import *
from cv.classes.game_objects import *
from cv.classes.framestate import Framestate
from multiprocessing.dummy import Pool as ThreadPool
from datetime import timedelta
from cv.workflow import other_functions as o
import numpy as np

jsonpickle.set_encoder_options('demjson', indent=4)
gap = recordclass('gap', 'len start end')
cycle = recordclass('cycle', 'frame cfg res teams')
pool = ThreadPool(8)

class Generator(object):
    def __init__(self, params, path, url):
        self.config = cp.get_config(params['cfg'])
        self.resources = r.Resources(self.config)
        self.path = path
        self.video = params['url'] + '.mp4'
        self.url = url
        self.created = params['date']
        self.gs = Gamestate(self.url, self.created)

        self.process_video()

    #Core Functionality
    def process_video(self):
        _capture = cv2.VideoCapture('%s%s' % (self.path, self.video))
        _fps = _capture.get(cv2.CAP_PROP_FPS)
        _max = int(_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        _ticks = 0

        while True:
            _ticks += 1

            @timeit
            def read_frame(capture, skip):
                capture.set(cv2.CAP_PROP_POS_FRAMES, skip)
                return capture.read()

            @timeit
            def process_frame(frame):
                frame = cv2.resize(frame, (1920, 1080), cv2.INTER_CUBIC)
                return Framestate(cycle(frame, self.config, self.resources, self.gs.teams), self.gs.ocr_, self.gs.teamjoin_)

            _flag, _frame = read_frame(_capture, _ticks * _fps)

            if _frame is None or _flag is None:
                self.next()
                break
            else:
                self.tick(process_frame(_frame), _ticks)
        return _ticks

    @timeit
    def tick(self, fs, ticks):
        self.gs.frames = ticks

        if fs.error: print(fs.error)

        if fs.valid is c.V_VALID:
            self.gs.gametime += 1
            self.update_gamestate(fs)
            self.gs.deadtime = 0
        elif fs.valid is c.V_PASS:
            self.gs.deadtime += 1
            self.gs.gametime += 1 if self.gs.gametime else 0
        elif fs.valid is c.V_INVALID:
            if self.gs.deadtime > c.GS_MAX_BAD_FRAMES and self.gs.gametime > 0:
                self.next()
            self.gs.deadtime += 1

    def update_gamestate(self, fs):
        if self.gs.ocr_:
            self.ocr(fs)
        elif self.gs.teamjoin_:
            self.joins(fs)
        else:
            self.recount_teams() #Count team members (could have changed since last update pending events)
            self.herobar(fs) #Process herobar events (compare gs to fs)
            self.killfeed(fs) #Process killfeed (compare gs to fs)
            self.merge_framestate(fs) #Merge across anything else (obj data, team state)

    # Core Helpers
    def next(self):
        self.fights()

        if len([x for x in self.gs.events if type(x) == EventFightStart]) > 1:
            self.json()
            self.log()

        self.gs = Gamestate(self.url, self.created)

    def json(self):
        _json = jsonpickle.encode(self.gs.events)
        _filename = o.get_file_name(self.video) + "." + str(time.time())
        _out = self.path + 'json/'

        os.makedirs(os.path.dirname(_out), exist_ok=True)
        with open(_out + _filename + ".txt", "w+") as text_file:
            text_file.write(_json)

    # Region Helpers
    def joins(self, fs):
        self.merge_framestate(fs)
        self.gs.events.append(EventMapLoaded(fs.map, self.gs))

        for team in fs.teams:
            for player in fs.teams[team]:
                self.gs.events.append(EventJoinedTeam(player, self.gs))

        self.gs.teamjoin_ = False

    def ocr(self, fs):
        self.merge_framestate(fs)
        self.gs.ocr_ = False

    def merge_framestate(self, fs):
        self.gs.objstate = fs.objstate  # Update objective state.
        self.gs.teams = fs.teams  # Update teams.

    # Region Processors
    def recount_teams(self):
        if not any([self.gs.ocr_, self.gs.teamjoin_]):
            for team in self.gs.teams.keys():
                for player in [x for x in self.gs.teams[team] if x.current_hero]:
                    if player.name + player.current_hero.name not in self.gs.death_filter:
                        player.state = c.S_ALIVE
                    elif self.gs.gametime < self.gs.death_filter[player.name + player.current_hero.name]:
                        if self.gs.gametime >= self.gs.death_filter[
                            player.name + player.current_hero.name] - c.KF_T_PLAYER_RESPAWN:
                            player.state = c.S_RUNBACK
                        else:
                            player.state = c.S_DEAD

    def killfeed(self, fs):
        def killfeed_line(t_line, gamestate):
            if t_line[0].type == c.EVENT_KILL:
                return EventKill(t_line, gamestate)
            elif t_line[0].type == c.EVENT_RESURRECT:
                return EventResurrect(t_line, gamestate)
            elif t_line[0].type == c.EVENT_MATRIX:
                return EventMatrix(t_line, gamestate)

        self.expired_filters()

        for index, line in enumerate(fs.killfeed):
            if line:
                invalid_kill = next((x.player for x in line if x.player.slot == -1), None)
                invalid_resser = next(
                    (x.player for x in line if x.type == c.EVENT_RESURRECT and x.entity.name != "Mercy"), None)
                invalid_ressed = False if not line[0].type == c.EVENT_KILL \
                    else next((x for x in fs.killfeed[index:]
                               if x is not None and x[len(x) - 1].type == c.EVENT_RESURRECTED
                               and x[len(x) - 1].player.name == line[len(line) - 1].player.name), False)

                if not invalid_kill and not invalid_resser and not invalid_ressed:
                    new_event = killfeed_line(line, self.gs)
                    self.update_filter(new_event)

    def herobar(self, fs):
        for team in fs.teams.keys():
            for player in fs.teams[team]:
                state_player = self.gs.teams[team][player.slot]
                state_player.swap_primer = player.swap_primer
                if player.current_hero.name != state_player.current_hero.name:
                    # Code to make sure we don't add hero swap events late into fights (roll em on)
                    _event = EventHeroSwap(player, state_player, self.gs)
                    self.gs.events.append(_event)
                    state_player.current_hero = player.current_hero
                elif player.current_hero.ult != state_player.current_hero.ult:
                    self.ult_event(player)
                    state_player.current_hero.ult = player.current_hero.ult
                elif player.current_hero.ult_pct < state_player.current_hero.ult_pct:
                    pass  # Player lost ultimate charge.. Add behaviour here.
                    # Presumably used ultimate. Need to check if it was tracked.

    def ult_event(self, player):
        if player.current_hero.ult:
            ult_reset = self.gs.gametime - next((x.gamestate.gametime for x in reversed(self.gs.events) if type(x) in (
                EventHeroSwap, EventJoinedTeam, EventUltUsed) and x.source.name == player.name))
            if player.current_hero.name == "DVa":
                self.event_handler_dva(player, ult_reset, EventUltGained)
            else:
                self.gs.events.append(EventUltGained(player, ult_reset, self.gs))
        else:
            ult_held = self.gs.gametime - next((x.gamestate.gametime for x in reversed(self.gs.events) if type(x) in (
                EventUltGained, EventHeroSwap, EventJoinedTeam) and x.source.name == player.name))
            if player.current_hero.name == "DVa":
                self.event_handler_dva(player, ult_held, EventUltUsed)
            else:
                self.gs.events.append(EventUltUsed(player, ult_held, self.gs))


    # Event Filters
    def update_filter(self, event):
        entity = event.target.name + (event.entity.name if hasattr(event, 'entity') else event.target.current_hero.name)
        if type(event) == EventKill:
            t_runback_mod = c.KF_T_PLAYER_RUNBACK if type(event.entity) is GameHero else 0
            if entity not in self.gs.death_filter or self.gs.gametime > (self.gs.death_filter[entity] - t_runback_mod):
                #self.create_fight_events()
                self.gs.events.append(event)
                self.gs.death_filter[entity] = (self.gs.gametime + c.KF_T_PLAYER_RESPAWN + t_runback_mod)
                self.recount_teams()
        elif type(event) == EventResurrect:
            if entity not in self.gs.resurrect_filter and entity in self.gs.death_filter:
                #self.create_fight_events()
                self.gs.events.append(event)
                self.gs.death_filter[entity] = -1
                self.gs.resurrect_filter[entity] = self.gs.gametime + c.KF_T_LINE_EXPIRATION
        elif type(event) == EventMatrix:
            if entity not in self.gs.matrix_filter:
                #self.create_fight_events()
                self.gs.events.append(event)
                self.gs.matrix_filter[entity] = self.gs.gametime + c.KF_T_LINE_EXPIRATION

    def expired_filters(self):
        def _filter(gs_filter):
            t_filter = dict()
            for key, value in gs_filter.items():
                if self.gs.gametime < value:
                    t_filter[key] = value
            return t_filter

        self.gs.death_filter = _filter(self.gs.death_filter)
        self.gs.resurrect_filter = _filter(self.gs.resurrect_filter)
        self.gs.matrix_filter = _filter(self.gs.matrix_filter)
        self.recount_teams()


    # Fight Management
    def fights(self):

        def first_kill():
            for i, e in enumerate(self.gs.events):
                if type(e) == EventKill:
                    return i

        if not first_kill(): return

        self.gs.events.insert(13, EventFightStart(self.gs.events[first_kill()].gamestate))
        _laststart = 13

        _gaps = self.calc_timegaps()

        if _gaps:
            for g in _gaps:
                _c = 0
                while True:
                    if len(self.gs.events) > _c:
                        if self.gs.events[_c] == g.start:
                            self.gs.events.insert(_c+1, EventFightEnd(
                                self.calculate_fight_outcome(
                                    self.gs.events[_laststart:_c]
                                )))
                            self.gs.events.insert(_c+2, EventFightStart(g.end.gamestate))
                            _laststart = _c+2
                            break
                        else: _c+= 1
                    else: break

        self.gs.events.insert(len(self.gs.events), EventFightEnd(
            self.calculate_fight_outcome(
                self.gs.events[_laststart:len(self.gs.events)])
        ))


    def calc_timegaps(self):
        _events = [x for x in self.gs.events if type(x) == EventKill]
        _gaps = []
        for i in range(0, len(_events)):
            if i-1 >= 0 and i+1 < len(_events):
                _gaps.append(gap(len=_events[i].gamestate.gametime-_events[i-1].gamestate.gametime, start=_events[i-1], end=_events[i]))

        _flen = np.array([x.len for x in _gaps])
        _pctile = max(np.percentile(_flen, 85), 10)
        _gaps = [x for x in _gaps if x.len > _pctile]

        return _gaps


    @staticmethod
    def calculate_fight_outcome(events):
         _end = events[len(events)-1].gamestate.instance()

         _rounds = [x.gamestate.objstate.round for x in events]
         _lefts = [x.gamestate.objstate.left_state for x in events]
         _rights = [x.gamestate.objstate.right_state for x in events]

         _end.objstate.round = max(set(_rounds), key=_rounds.count)
         _end.objstate.left_state = max(set(_lefts), key=_lefts.count)
         _end.objstate.right_state = max(set(_rights), key=_rights.count)

         _left = len([x for x in _end.teams[c.TEAM_LEFT] if x.state == c.S_ALIVE])
         _right = len([x for x in _end.teams[c.TEAM_RIGHT] if x.state == c.S_ALIVE])

         if _left == _right: #Tiebreakers are important
             if _end.objstate.round == '1': #Attackers benefit from respawns on A1
                 _result = c.TEAM_LEFT if _end.objstate.left_state == c.TS_ATTACK else c.TEAM_RIGHT
             elif _end.objstate.round == '3': #Defenders benefit from respawns on D3
                 _result = c.TEAM_LEFT if _end.objstate.left_state == c.TS_DEFENSE else c.TEAM_RIGHT
             else: #KOTH or second point (equal respawn adv in theory)
                 _left = len([x for x in events if type(x) == EventKill and x.source.team == c.TEAM_LEFT and x.target.current_hero.name == x.entity.name])
                 _result = len([x for x in events if type(x) == EventKill and x.source.team == c.TEAM_RIGHT and x.target.current_hero.name == x.entity.name])
                 if _left == _right: #First kill will have respawn adv.
                    _result = next(x.source.team for x in events if type(x) == EventKill)
                 else: #Whoever got more kills probably wins (runback is slow on 2nd)
                    _result = c.TEAM_LEFT if _left > _right else c.TEAM_RIGHT
         else:
             _result = c.TEAM_LEFT if _left > _right else c.TEAM_RIGHT

         return _result, _end

    #Edge Case Functions
    def event_handler_dva(self, player, timer, event):
        r_events = list(reversed(self.gs.events))

        def mech_state():
            for idx, past_event in enumerate(r_events):
                if (self.gs.gametime - past_event.gamestate.gametime) > 30:
                    return c.E_DVA_MECH
                if type(past_event) == EventResurrect and past_event.target.name == player.name:
                    return c.E_DVA_BABY  # Remeched after a rez.
                elif type(past_event) == EventUltUsed and past_event.source.name == player.name:
                    return c.E_DVA_BABY  # Remeched after an ult.
                elif type(past_event) == EventKill and past_event.target.name == player.name:
                    if past_event.target.current_hero.name == past_event.entity.name:
                        return c.E_DVA_MECH  # Ulted after coming out of spawn (as a mech)
                    else:
                        return c.E_DVA_BABY
            return c.E_DVA_MECH

        if mech_state() == c.E_DVA_MECH:
            self.gs.events.append(event(player, timer, self.gs))

    #Basic Logging
    def log(self):
        def get_player_string(t_player):
            return t_player.name + " (" + t_player.current_hero.name + "/" + t_player.team + ")"

        eventText = ""

        for event in self.gs.events:
            eventText += "\n[" + str(timedelta(seconds=event.gamestate.gametime)) + "] "
            if type(event) == EventMapLoaded:
                eventText += "Loaded map and retrieved player names"
            elif type(event) == EventUltUsed:
                eventText += "%s used their ultimate" % get_player_string(event.source)
            elif type(event) == EventUltGained:
                eventText += "%s ultimate is now online" % get_player_string(event.source)
            elif type(event) == EventResurrect:
                eventText += "%s resurrected teammate %s" % (
                get_player_string(event.source), get_player_string(event.target))
            elif type(event) == EventMatrix:
                eventText += "%s matrixed ultimate of %s" % (
                get_player_string(event.source), get_player_string(event.target))
            elif type(event) == EventHeroSwap:
                eventText += "%s has swapped heroes to %s" % (
                get_player_string(event.target), event.source.current_hero.name)
            elif type(event) == EventFightEnd:
                eventText += "Fight has ended - %s was the winner (Obj: %s Left: %s Right: %s)" % (
                event.result, event.gamestate.objstate.round, event.gamestate.objstate.left_state,
                event.gamestate.objstate.right_state)
            elif type(event) == EventFightStart:
                eventText += "Fight has started"
            elif type(event) == EventJoinedTeam:
                eventText += "%s has joined the server" % (get_player_string(event.source))
            elif type(event) == EventKill:
                unitText = "%s" % (
                    '' if event.target.current_hero.name == event.entity.name else " [" + event.entity.name + "]")
                eventText += "%s killed %s with %s" % (
                get_player_string(event.source), get_player_string(event.target) + unitText, event.ability.name)
                for player in event.assists:
                    eventText += "[%s]" % get_player_string(player)

        print(eventText)

        _out = self.path + c.LAB_LOGS
        os.makedirs(os.path.dirname(_out), exist_ok=True)

        with open(_out + str(time.time()) + ".log", "w+") as log:
            log.write(eventText + '\n')