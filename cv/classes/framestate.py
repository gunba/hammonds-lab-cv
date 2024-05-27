import re
from multiprocessing.dummy import Pool as ThreadPool
from cv.classes.frame_regions import *
from cv.classes.game_objects import *
from cv.classes.game_events import *
from cv.workflow import other_functions as o
from cv.workflow import image_functions as i
from recordclass import recordclass
from settings import constants as c
import time
import cv2

np.seterr(all='raise')

match = recordclass('match', 'entity min x y color')
rect = recordclass('rect', 'xmin ymin xmax ymax')
pool = ThreadPool(16)
ocr_id = 0

class Framestate(object):
    def __init__(self, cycle = None, ocr=False, teamjoin=False):

        if cycle:
            self.frame = cycle.frame
            self.teams = cycle.teams
            self.cfg = cycle.cfg
            self.res = cycle.res

        self.teamjoin = teamjoin
        self.ocr = ocr

        self.regions = None
        self.killfeed = None
        self.map = None
        self.valid = None
        self.objstate = None

        if self.frame is not None:
            #Create regions and see if we have a frame
            self.create_frame_regions()
            #o.cv_error(self.regions["Herobar"][c.TEAM_LEFT].slice_left[0][c.MOD_GRAY], time.time())
            self.valid, self.error = self.validate_frame()

            if self.valid == c.V_VALID:
                #We have an objective. Process the frame.
                self.process_herobar()
                self.process_killfeed()

                #Act on generator given params
                if self.ocr: self.process_namebar()
                if self.teamjoin: self.map = cv2.resize(self.frame, (1280, 720), cv2.INTER_CUBIC)


    def validate_frame(self):
        #TODO: Are we the baddies?
        if self.ocr and not self.validate_gamestart(): return c.V_INVALID, 'Invalid frame: Game hasn\'t started yet'

        # #TODO: Fix replay detection.
        # _replay = find_template_match(self.regions["Replay"].image, self.res.REPLAY, threshold=self.cfg.TM_THRESH_REPLAY, single=True)
        # if _replay: return c.V_INVALID, 'Invalid frame: Replay watermark detected in frame'

        if not self.get_objective_data(): return c.V_INVALID, 'Invalid frame: No objective found in frame'

        for idx, herobar in enumerate(self.regions["Herobar"]):
            _existing = list()
            _none = 0
            for idy, hero_slice in enumerate(self.regions["Herobar"][herobar].slice_right):
                _dead = True if self.teams and self.teams[c.TEAM_LEFT if idx == 0 else c.TEAM_RIGHT][idy].state == c.S_DEAD else False
                if not _dead:
                    _hero = find_template_match(hero_slice, self.res.HB_HEROES.values(), single=True, threshold=self.cfg.TM_THRESH_HEROBAR)
                    if _hero:
                        if _hero.entity.name in _existing:
                            return c.V_INVALID, 'INVALID: Same hero selected twice on one team.'
                        else:
                            _existing.append(_hero.entity.name)
                    else:
                        if self.ocr: _none += 1
                        if _none > 2: return  c.V_INVALID, 'INVALID: Multiple players are missing a hero.'

        if self.ocr: o.cv_error(self.frame, time.time())

        return c.V_VALID, None

        # for idx, herobar in enumerate(self.regions["Herobar"]):
        #     for idy, hero_slice in enumerate(self.regions["Herobar"][herobar].slice_right):
        #         _bmatch = get_tm_min(hero_slice[c.MOD_GRAY], self.res.NONE_HERO[c.TEAM_LEFT])
        #         _rmatch = get_tm_min(hero_slice[c.MOD_GRAY], self.res.NONE_HERO[c.TEAM_RIGHT])
        #         _nmin = min(_bmatch.min, _rmatch.min)
        #         if self.cfg.TM_THRESH_NONEHERO > _nmin: return c.V_PASS, 'INVALID: Player with no hero selected'

    def validate_gamestart(self):
        #Can scan both - but realistically left is more reliable esp for OWL..
        _match = get_tm_min(self.regions["Herobar"][c.TEAM_LEFT].slice_left[0][c.MOD_GRAY], self.res.ZERO_PCT_ULT[self.cfg.UI_COLOR_MATCHING][c.TEAM_LEFT])
        return _match.min > self.cfg.TM_THRESH_ZERO_ULT

    def create_frame_regions(self):
        _t = time.perf_counter()

        frame = Frame(self.frame)

        herobar_left = Herobar(frame.image[self.cfg.UI_HEROBAR['Y1']:self.cfg.UI_HEROBAR['Y2'], self.cfg.UI_HEROBAR['LEFT_X1']:self.cfg.UI_HEROBAR['LEFT_X2']])
        herobar_right = Herobar(frame.image[self.cfg.UI_HEROBAR['Y1']:self.cfg.UI_HEROBAR['Y2'], self.cfg.UI_HEROBAR['RIGHT_X1']:self.cfg.UI_HEROBAR['RIGHT_X2']])
        names_left = Namebox(frame.image[self.cfg.UI_NAMEBOX['Y1']:self.cfg.UI_NAMEBOX['Y2'], self.cfg.UI_NAMEBOX['LEFT_X1']:self.cfg.UI_NAMEBOX['LEFT_X2']])
        names_right = Namebox(frame.image[self.cfg.UI_NAMEBOX['Y1']:self.cfg.UI_NAMEBOX['Y2'], self.cfg.UI_NAMEBOX['RIGHT_X1']:self.cfg.UI_NAMEBOX['RIGHT_X2']])
        obj_left = Objectives(frame.image[self.cfg.UI_OBJ['Y1']:self.cfg.UI_OBJ['Y2'], self.cfg.UI_OBJ['X1']:self.cfg.UI_OBJ['XM']])
        obj_right = Objectives(frame.image[self.cfg.UI_OBJ['Y1']:self.cfg.UI_OBJ['Y2'], self.cfg.UI_OBJ['XM']:self.cfg.UI_OBJ['X2']])
        obj_center = Objectives(frame.image[self.cfg.UI_OBJ['CENTER_Y1']:self.cfg.UI_OBJ['CENTER_Y2'], self.cfg.UI_OBJ['CENTER_X1']:self.cfg.UI_OBJ['CENTER_X2']])
        killfeed = Killfeed(frame.image[self.cfg.UI_KILLFEED['Y1']:self.cfg.UI_KILLFEED['Y2'], self.cfg.UI_KILLFEED['X1']:self.cfg.UI_KILLFEED['X2']])

        self.regions = {"Frame": frame,
                      "Herobar": {c.TEAM_LEFT: herobar_left, c.TEAM_RIGHT: herobar_right},
                      "Names": {c.TEAM_LEFT: names_left, c.TEAM_RIGHT: names_right},
                      "Objective": {c.TEAM_LEFT: obj_left, c.TEAM_RIGHT: obj_right, "Center": obj_center},
                      "Killfeed": killfeed}

    def get_objective_data(self):
        obj_center = self.regions["Objective"]["Center"].image
        obj_left = self.regions["Objective"][c.TEAM_LEFT].image
        obj_right = self.regions["Objective"][c.TEAM_RIGHT].image

        _obj = ObjectiveState()

        def set_obj_state(obj, left = None, right = None, round = None):
            if round: obj.round = round

            obj.left_state = left
            obj.right_state = right
            obj.valid = True

        _koth = find_template_match(obj_center, self.res.OBJ_KOTH_CAPPED_LEFT + self.res.OBJ_KOTH_CAPPED_RIGHT + self.res.OBJ_KOTH_NOT_CAPPED, threshold=self.cfg.TM_THRESH_OBJ, single=True, color=False)

        if _koth:
            _obj.valid = True
            _obj.round = _koth.entity.state
            _obj.left_state = _obj.right_state = c.TS_ROLLOUT

            if _obj.round != "LOCKED":
                avg_color = a.get_edge_color(obj_center[c.MOD_BGR][_koth.y:_koth.y + _koth.entity.image[c.HEIGHT], _koth.x:_koth.x + _koth.entity.image[c.WIDTH]], 6, 31, 5, 22, self.cfg.UI_COLOR_MATCHING)
                if self.cfg.UI_COLOR_MATCHING == c.B_BR:
                    if avg_color[0] > 180:
                        set_obj_state(_obj, left=c.TS_DEFENSE, right=c.TS_ATTACK)
                    elif avg_color[2] > 180:
                        set_obj_state(_obj, left=c.TS_ATTACK, right=c.TS_DEFENSE)
                elif self.cfg.UI_COLOR_MATCHING == c.B_WG:
                    avg_color = np.average(avg_color)
                    if avg_color > 190:
                        set_obj_state(_obj, left=c.TS_DEFENSE, right=c.TS_ATTACK)
                    elif avg_color > 100:
                        set_obj_state(_obj, left=c.TS_ATTACK, right=c.TS_DEFENSE)
                    #o.cv_error(obj_center[c.MOD_BGR][_koth.y:_koth.y + _koth.entity.image[c.HEIGHT], _koth.x:_koth.x + _koth.entity.image[c.WIDTH]], str(avg_color) + 'X' + str(time.time()))
        else:
            _left = find_template_match(obj_left, self.res.OBJ_ROUND_SCORE_LEFT + self.res.OBJ_ROUND_SCORE_RIGHT, threshold=self.cfg.TM_THRESH_OBJ, single=True, color=False)
            _right = find_template_match(obj_right, self.res.OBJ_ROUND_SCORE_LEFT + self.res.OBJ_ROUND_SCORE_RIGHT, threshold=self.cfg.TM_THRESH_OBJ, single=True, color=False)
            if None not in (_left, _right):
                #Found a match on both sides. Need to figure out which is real.
                left_color = a.get_edge_color(obj_left[c.MOD_BGR][_left.y:_left.y + _left.entity.image[c.HEIGHT], _left.x:_left.x + _left.entity.image[c.WIDTH]], 5, 32, 14, 36, self.cfg.UI_COLOR_MATCHING)
                right_color = a.get_edge_color(obj_right[c.MOD_BGR][_right.y:_right.y + _right.entity.image[c.HEIGHT], _right.x:_right.x + _right.entity.image[c.WIDTH]], 5, 32, 14, 36, self.cfg.UI_COLOR_MATCHING)
                if self.cfg.UI_COLOR_MATCHING == c.B_BR:
                    if left_color[0] > right_color[2]:
                        set_obj_state(_obj, round=_left.entity.state, left=c.TS_ATTACK, right=c.TS_DEFENSE)
                    else:
                        set_obj_state(_obj, round=_right.entity.state, left=c.TS_DEFENSE, right=c.TS_ATTACK)
                elif self.cfg.UI_COLOR_MATCHING == c.B_WG:
                    if left_color > right_color:
                        set_obj_state(_obj, round=_left.entity.state, left=c.TS_ATTACK, right=c.TS_DEFENSE)
                    else:
                        set_obj_state(_obj, round=_right.entity.state, left=c.TS_DEFENSE, right=c.TS_ATTACK)
                    # o.cv_error(obj_left[c.MOD_BGR][_left.y:_left.y + _left.entity.image[c.HEIGHT], _left.x:_left.x + _left.entity.image[c.WIDTH]], str(left_color) + 'L' + str(time.time()))
                    # o.cv_error(obj_right[c.MOD_BGR][_right.y:_right.y + _right.entity.image[c.HEIGHT], _right.x:_right.x + _right.entity.image[c.WIDTH]], str(right_color) + 'R' + str(time.time()))
            elif _left:
                set_obj_state(_obj, round=_left.entity.state, left=c.TS_ATTACK, right=c.TS_DEFENSE)
            elif _right:
                set_obj_state(_obj, round=_right.entity.state, left=c.TS_DEFENSE, right=c.TS_ATTACK)
            else:
                _obj.valid = False

        self.objstate = _obj
        return _obj.valid

    # Computer Vision
    def process_herobar(self):
        _t = time.perf_counter()
        _herobar = self.regions["Herobar"]

        def process_herobar_thread(player):
            _player = player.instance()
            _state = self.teams[_player.team][_player.slot].instance()
            _thresh = c.TM_MAX_THRESH if self.teamjoin else self.cfg.TM_THRESH_HEROBAR
            _match = find_template_match(_herobar[_player.team].slice_right[_player.slot], self.res.HB_HEROES.values(), threshold=_thresh, single=True)

            if _match:
                # Player has picked first hero
                if not _player.current_hero:
                    _player.current_hero = GameHero(_match.entity.name)
                    _player.swap_primer = GameHero(_match.entity.name)
                # Player may have swapped - update primer
                elif _player.swap_primer.name != _match.entity.name:
                    _player.swap_primer = GameHero(_match.entity.name)
                # Player definitely swapped - update hero
                elif _player.current_hero.name != _match.entity.name:
                    _player.current_hero = GameHero(_match.entity.name)
                else:
                    _player.current_hero = _state.current_hero.instance()
            else:
                _player.current_hero = _state.current_hero.instance()

            _ult = find_template_match(_herobar[_player.team].slice_left[_player.slot], self.res.ULT_INDICATORS, single=True)

            if _ult.min > self.cfg.TM_THRESH_ULT:
                _player.current_hero.ult = False
                if self.cfg.UI_COLOR_MATCHING == c.B_BR:
                    #TODO: This shit is fucking slooooow. 50% of our processing time right here.
                    _lum = _herobar[_player.team].slice_pct[_player.slot][c.MOD_GRAY].mean()
                    _ultpct = find_template_match(_herobar[_player.team].slice_pct[_player.slot], self.res.ULT_PCT.values(), threshold=self.cfg.TM_THRESH_ULT_NUM, multi=True, overlap=200)
                    if _ultpct:
                        _ultpct.sort(key=lambda x: x.x)
                        _numbers = [x.entity.name for x in _ultpct]
                        _numbers = "".join(_numbers)
                        _player.current_hero.ult_pct = int(_numbers)
                        correct_missed_ults(_player, _state, _numbers, _lum) #Hack to correct missed ults.
                        #o.cv_error(herobar[player.team].slice_pct[player.slot][c.MOD_GRAY], _numbers + "X" + str(time.time()))
            else:
                _player.current_hero.ult = True
                _player.current_hero.ult_pct = -1

            return _player

        def correct_missed_ults(player, state, _numbers, _lum):
            if state.current_hero and state.current_hero.ult_pct > 80 \
                    and player.current_hero.ult_pct < state.current_hero.ult_pct \
                    and player.current_hero.name == state.current_hero.name:
                print("Artificially created ult event " + str(player.current_hero.ult_pct) + " " + str(state.current_hero.ult_pct))
                player.current_hero.ult = True
                o.cv_error(_herobar[player.team].slice_pct[player.slot][c.MOD_GRAY], _numbers + "X" + str(time.time()) + "X" + str(_lum))

        _teams = dict()
        for team in self.teams:
            _teams[team] = pool.map(process_herobar_thread, self.teams[team])

        self.teams = _teams

    def process_namebar(self):
        _t = time.perf_counter()
        nameboxes = self.regions["Names"]
        teams = self.teams

        def process_namebar_thread(player):
            name = a.ocr_image(nameboxes[player.team].namebox_slice[player.slot], self.cfg.UI_FONT)
            player.name_ocr = a.numpy_to_jpg(nameboxes[player.team].namebox_slice[player.slot])
            name = re.sub(r'[^A-Z0-9]', '', name)

            if len(name) <= 2:
                global ocr_id
                player.name = "UNKNOWN_" + player.team + "_" + str(player.slot+1) + "_" + str(ocr_id)
                ocr_id +=1
            else:
                player.name = name

            return player

        for team in teams:
            teams[team] = pool.map(process_namebar_thread, teams[team])


    def process_killfeed(self):
        _t = time.perf_counter()

        #TODO: Cleanup.
        killfeed = self.regions["Killfeed"]
        teams = self.teams

        _heroes = set([x.current_hero.name for x in teams[c.TEAM_LEFT] + teams[c.TEAM_RIGHT]])
        _bigk = [self.res.KF_KILLS[y] for y in _heroes]
        _smallu = [x for x in self.res.KF_SMALL_UNITS.values() if x.parent in _heroes]
        _smallk = [self.res.KF_SMALL_KILLS[y] for y in _heroes]
        _smallm = [self.res.KF_MATRIX[y] for y in _heroes if y in self.res.KF_MATRIX]

        def process_killfeed_thread(pair):

            def entity_to_player(m, team):
                return next((x for x in teams[team] if
                             ((x.current_hero.name == m.entity.name) or (m.entity.name in self.res.KF_SMALL_UNITS and self.res.KF_SMALL_UNITS[m.entity.name].parent == x.current_hero.name))),
                            Player(-1, team, m.entity))

            if len(pair) < 2: return None

            res = list()

            _type = c.KF_BIG if type(pair[1].entity).__name__ == 'Kill' else c.KF_SMALL if type(pair[1].entity).__name__ == 'Unit' else c.KF_MATRIX

            if _type == c.KF_MATRIX:
                res.append(KillfeedEvent(GameHero(pair[0].entity.name), entity_to_player(pair[0], pair[0].entity.team), c.EVENT_MATRIX))
                res.append(KillfeedEvent(GameAbility('Defense Matrix'), res[0].player, c.EVENT_ABILITY))
                res.append(KillfeedEvent(GameHero(pair[1].entity.name), entity_to_player(pair[1], pair[1].entity.team), c.EVENT_MATRIXED))
            else:
                _line = i.resize_models(killfeed.image, pair[0].y - c.KF_CONST[_type]["LINE_Y1"], pair[0].y + c.KF_CONST[_type]["LINE_Y2"], pair[0].x + c.KF_CONST[_type]["LINE_X1"], pair[1].x - c.KF_CONST[_type]["LINE_X2"])

                #Assist ROI is reduced Y axis + end of kill -> start of arrow buffer
                _assist = i.resize_models(_line, c.KF_CONST[_type]["ASSIST_Y1"], c.KF_CONST[_type]["ASSIST_Y2"], 0, max(1, _line[c.WIDTH] - c.KF_CONST[_type]["ASSIST_X2"]))
                _maxw = 0

                if _assist[c.WIDTH] > 0:
                    _valid = [x for x in (self.res.KF_ASSISTS if _type == c.KF_BIG else self.res.KF_SMALL_ASSISTS).values() if x.name in (y.current_hero.name for y in teams[pair[0].entity.team])]
                    _assists = find_template_match(_assist, _valid, threshold=self.cfg.TM_THRESH_ASSIST)

                    if _assists:
                        for assist in _assists:
                            pair.append(assist)

                        _maxw = max(x.x for x in _assists) + c.KF_CONST[_type]["ASSIST_STEP"]

                # Ability ROI is full Y axis + last assist - start of arrow icon
                _abilities = i.resize_models(_line, 0, _line[c.HEIGHT], _maxw+c.KF_CONST[_type]["ABILITY_X1"], _line[c.WIDTH] - c.KF_CONST[_type]["ABILITY_X2"])

                # Lets find an attack.
                _ability = self.res.A_ATTACK

                # TODO: Detect color of crit here (very easy but not very useful)
                _ability_set = [x for x in (self.res.KF_ABILITIES if _type == c.KF_BIG else self.res.KF_SMALL_ABILITIES).values() if x.parent == pair[0].entity.name]

                if _abilities[c.WIDTH] > c.KF_CONST[_type]["MAX_ATTACK"]:
                    _ability = find_template_match(_abilities, _ability_set, single=True) or self.res.A_ATTACK

                pair.insert(1, _ability)

                # Build actual killfeed events from discovered objects
                p_kill = pair[0]
                p_ability = pair[1]
                p_death = pair[2]

                res.append(KillfeedEvent(GameHero(p_kill.entity.name), entity_to_player(p_kill, p_kill.entity.team), c.EVENT_KILL if p_kill.entity.team != p_death.entity.team else c.EVENT_RESURRECT))
                res.append(KillfeedEvent(GameAbility(p_ability.entity.name), res[0].player, c.EVENT_ABILITY))
                res.append(KillfeedEvent(GameHero(p_death.entity.name) if p_death.entity.name == entity_to_player(p_death, p_death.entity.team).current_hero.name else GameUnit(p_death.entity.name),
                                         entity_to_player(p_death, p_death.entity.team), c.EVENT_DEATH if p_kill.entity.team != p_death.entity.team else c.EVENT_RESURRECTED))

                for assist in pair[3:]:
                    res.insert(2, KillfeedEvent(GameHero(assist.entity.name), entity_to_player(assist, p_kill.entity.team), c.EVENT_ASSIST))

            return res

        _kills = find_template_match(killfeed.image, _bigk, threshold=self.cfg.TM_THRESH_KILL, multi=True)
        _roi = i.resize_models(killfeed.image, 0, killfeed.image[c.HEIGHT], killfeed.image[c.WIDTH]-self.cfg.UI_KILLFEED['SMALL'], killfeed.image[c.WIDTH])
        _units = find_template_match(_roi, _smallu + _smallm, threshold=self.cfg.TM_THRESH_SMALL_KILL, multi=True)

        _kills = list() if not _kills else _kills
        _units = list() if not _units else _units

        _units = self.find_smallfeed_pairs(_units, _kills, _smallk)

        events = _kills + _units

        if len(events) > 1:
            events = self.assign_killfeed_teams(events)
            pairs = self.pair_killfeed_matches(events)
            self.killfeed = list(reversed(pool.map(process_killfeed_thread, pairs)))
        else:
            self.killfeed = list()

    def find_smallfeed_pairs(self, units, kills, entities):
        _t = time.perf_counter()

        killfeed = self.regions["Killfeed"]

        _kills = list()
        _shift = (self.cfg.UI_KILLFEED['X2'] - self.cfg.UI_KILLFEED['X1']) - self.cfg.UI_KILLFEED['SMALL']

        for unit in units: _kills.append(Match(unit.entity, unit.min, (unit.x+_shift, unit.y)))

        for unit in units:
            overlap = next((x for x in kills if x.y+46 > unit.y > x.y), None)
            if not overlap:
                _roi = i.resize_models(killfeed.image, unit.y-6, unit.y+22, 0, killfeed.image[c.WIDTH])
                _match = find_template_match(_roi, entities, threshold=self.cfg.TM_THRESH_SMALL_KILL, single=True)
                if _match:
                    _match.y = unit.y
                    _kills.append(_match)

        return _kills

    @staticmethod
    def pair_killfeed_matches(kills):
        _t = time.perf_counter()
        _pairs = list()
        _matches = list()

        for m in kills:
            if m not in _matches:
                pair = next((x for x in kills if x != m and abs(m.y - x.y) < 3), None)

                _line = list()
                _matches.append(m)
                _line.append(m)

                if pair:
                    _matches.append(pair)
                    _line.append(pair)
                    _line.sort(key=lambda x: x.x)

                _pairs.append(_line)

        _pairs.sort(key=lambda x: x[0].y)
        return _pairs

    def assign_killfeed_teams(self, events):
        killfeed_roi = self.regions["Killfeed"]
        _pairs = list()

        def find_team_color(m):

            #FOR OWL AND CONTENDERS - GET OUTSIDE OF KILLFEED FRAME
            if self.cfg.UI_COLOR_MATCHING == c.B_WG:
                _mod = c.MOD_GRAY
                _target = killfeed_roi.image[_mod][m.y - 6:m.y + m.entity.image[c.HEIGHT] + 6, m.x - 6:m.x + m.entity.image[c.WIDTH] + 6]
                w, h = a.get_size(_target)
                _color = a.get_edge_color(_target, 2, h - 3, 2, w - 3, self.cfg.UI_COLOR_MATCHING)
                team = None if 175 > _color > 165 else c.TEAM_LEFT if _color > 170 else c.TEAM_RIGHT
                #o.cv_error(killfeed_roi.image[c.MOD_BGR][m.y - 6:m.y + m.entity.image[c.HEIGHT] + 6, m.x - 6:m.x + m.entity.image[c.WIDTH] + 6], str(_color) + "." + (team if team is not None else "None"))
                return team

            #FOR LIVE - GET BORDER FRAME (EXPECTED QUALITY HIGHER ANYWAY)
            elif self.cfg.UI_COLOR_MATCHING == c.B_BR:
                _mod = c.MOD_BGR
                _target = killfeed_roi.image[_mod][m.y - 3:m.y + m.entity.image[c.HEIGHT] + 3, m.x - 3:m.x + m.entity.image[c.WIDTH] + 3]
                w, h = a.get_size(_target)
                _color = a.get_edge_color(_target, 2, h - 3, 2, w - 3, self.cfg.UI_COLOR_MATCHING)
                return c.TEAM_LEFT if (_color[0] + _color[1]) / 2 > _color[2] else c.TEAM_RIGHT

        for _match in events:
            _match.entity.team = find_team_color(_match)
            if _match.entity.team:
                _pairs.append(_match)

        return _pairs



def find_template_match(image, entities, method=cv2.TM_CCOEFF_NORMED, threshold=c.TM_MAX_THRESH, multi=False, single=False, color=True, overlap=0):
    _matches = list()

    def check_overlap(_m, matches):
        _xrect = rect(xmin=_m.x, ymin=_m.y, xmax=_m.x + _m.entity.image[c.WIDTH], ymax=_m.y + _m.entity.image[c.HEIGHT])
        for target in matches:
            _yrect = rect(xmin=target.x, ymin=target.y, xmax=target.x+target.entity.image[c.WIDTH], ymax=target.y+target.entity.image[c.HEIGHT])
            if area(_xrect, _yrect):
                if _m.min > target.min: #? This is a child overlap.
                    return True
                if _m.min == target.min and matches.index(_m) > matches.index(target):
                    return True
        return False #This _m has no overlap or is parent.

    def area(one, two):  #Check if rects overlap (in theory)
        dx = min(one.xmax, two.xmax) - max(one.xmin, two.xmin)
        dy = min(one.ymax, two.ymax) - max(one.ymin, two.ymin)
        if (dx >= 0) and (dy >= 0):
            return (dx * dy) > overlap

    def tm_thread(entity):
        _m = list()
        if entity.image[c.MOD_GRAY].shape[1] > image[c.MOD_GRAY].shape[1]:
            pass
        else:
            _t = get_tm_min(image[c.MOD_GRAY], entity.image[c.MOD_GRAY], method, entity, threshold if multi else False)
            if _t:
                if type(_t) == list:
                    _m += _t
                else:
                    _m.append(_t)
                # _matches += _t if type(_t) == list else _matches.append(_t)
        return _m

    _matches = list(pool.map(tm_thread, entities))
    _matches = [x for y in _matches for x in y]

    if not multi: #Multi filters in the TM (np.where -> thresh)
        _matches = [x for x in _matches if x.min < threshold]

    if len(_matches) > 0: _matches = [x for x in _matches if not check_overlap(x, _matches)]

    # Color filtering if BGR image is found.
    if color:
        for m in _matches:
            if c.MOD_BGR in m.entity.image:
                source = a.quad(image[c.MOD_BGR][m.y:m.y + m.entity.image[c.HEIGHT], m.x:m.x + m.entity.image[c.WIDTH]])
                m.color = max([a.compare_color(m.entity.image[c.MOD_QUAD][x], source[x]) for x in range(0, 3)])
            else:
                m.color = 0

        _filtered = [m for m in _matches if m.color >= c.CM_COLOR_THRESH]
        _matches = [m for m in _matches if m.color < c.CM_COLOR_THRESH]

        #for m in _filtered: o.cv_error(image[c.MOD_BGR][m.y:m.y + m.entity.image[c.HEIGHT], m.x:m.x + m.entity.image[c.WIDTH]], str(m.color) + '.' + m.entity.name + '.' + str(time.time()))

    # Some objects are mutable/changed during runtime.
    def instance_thread(_m):
        if hasattr(_m.entity, 'instance'):
            _m.entity = _m.entity.instance()

    # Some objects are mutable/changed during runtime.
    list(pool.map(instance_thread, _matches))

    # Sort by matches by min thresh
    _matches.sort(key=lambda x: x.min)

    # Return format as requested (single or multiple)
    if single:
        return None if not _matches else _matches[0]
    else:
        return _matches

def get_tm_min(image, template, method=cv2.TM_CCOEFF_NORMED, entity=None, multi=False):
    if template.shape[1] > image.shape[1] or template.shape[0] > image.shape[0]: return match(entity=entity, min=1, x=0, y=0, color=0)

    res = cv2.matchTemplate(image, template, method)

    if multi:
        return [match(entity=entity,  min=1-res[pos[1]][pos[0]], x=pos[0], y=pos[1], color=0) for pos in zip(*np.where(1-res < multi)[::-1])]
    else:
        _, _min, _, _pos = cv2.minMaxLoc(res)
        return match(entity=entity, min=1-_min, x=_pos[0], y=_pos[1], color=0)




