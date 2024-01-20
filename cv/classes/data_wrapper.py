from dateutil import parser
from cv.classes.game_events import *

class Round(object):
    def __init__(self, map, left_team, right_team, region, patch, video, created):
        self.map = map
        self.left_team = left_team
        self.right_team = right_team
        self.region = region
        self.patch = patch
        self.fights = list()
        self.video = video
        self.created = parser.parse(created).strftime('%Y-%m-%d %H:%M:%S')

class Fight(object):
    def __init__(self, event, data):
        self.winner = 0 if event.result == c.TEAM_LEFT else 1 if event.result == c.TEAM_RIGHT else 2
        self.left_side = c.MAP_SIDE[event.gamestate.objstate.left_state]
        self.right_side = c.MAP_SIDE[event.gamestate.objstate.right_state]
        self.objective = c.MAP_OBJ[event.gamestate.objstate.round] if event.gamestate.objstate.round in c.MAP_OBJ else event.gamestate.objstate.round
        self.killfeed_events = list()
        self.herobar_events = list()
        self.fight_start = Gamestate(data[0].gamestate)
        self.fight_end = Gamestate(event.gamestate)

        # TODO: Better solution (move fight start frame to first event)
        self.fight_start.frames = data[1].gamestate.frames

        for event in data:
            if type(event) in (EventJoinedTeam, EventHeroSwap, EventUltGained, EventUltUsed):
                self.herobar_events.append(Herobar_Event(event))
            elif type(event) in (EventKill, EventResurrect, EventMatrix):
                self.killfeed_events.append(Killfeed_Event(event))



class Gamestate(object):
    def __init__(self, gamestate):
        self.slots = list()
        for player in gamestate.teams[c.TEAM_LEFT] + gamestate.teams[c.TEAM_RIGHT]:
            if player.current_hero: self.slots.append(PlayerState(player))
        self.gametime = gamestate.gametime
        self.frames = gamestate.frames

class PlayerState(object):
    def __init__(self, player):
        self.name = player.name
        self.hero = player.current_hero.name
        self.ult = player.current_hero.ult
        self.state = player.state
        self.team = 0 if player.team == c.TEAM_LEFT else 1
        self.slot = player.slot

class Killfeed_Event(object):
    def __init__(self, event):
        self.type = type(event).__name__
        self.left_slot = event.source.slot
        self.left_name = event.source.name
        self.left_hero = event.source.current_hero.name
        self.left_team = 0 if event.source.team == c.TEAM_LEFT else 1
        self.left_ult = event.source.current_hero.ult
        self.left_num = len([x for x in event.gamestate.teams[event.source.team] if x.state == c.S_ALIVE])
        self.ability = event.ability.name
        self.critical = 0
        self.entity = event.entity.name if hasattr(event, 'entity') else None
        self.right_slot = event.target.slot
        self.right_name = event.target.name
        self.right_hero = event.target.current_hero.name
        self.right_team = 0 if event.target.team == c.TEAM_LEFT else 1
        self.right_ult = event.target.current_hero.ult
        self.right_num = len([x for x in event.gamestate.teams[c.TEAM_RIGHT if event.source.team == c.TEAM_LEFT else c.TEAM_LEFT] if x.state == c.S_ALIVE])
        self.gametime = event.gamestate.gametime
        self.frames = event.gamestate.frames
        self.assists = list()

        for assist in event.assists:
            self.assists.append(Assist(assist))

class Assist(object):
    def __init__(self, assist):
        self.name = str(assist.name)
        self.hero = assist.current_hero.name
        self.ult = assist.current_hero.ult
        self.slot = assist.slot
        #..EVENT

class Herobar_Event(object):
    def __init__(self, event):

        enemy_team = c.TEAM_LEFT if event.source.team == c.TEAM_RIGHT else c.TEAM_RIGHT
        self.type = type(event).__name__
        self.slot = event.source.slot
        self.name = event.source.name
        self.hero = event.source.current_hero.name
        self.team = 0 if event.source.team == c.TEAM_LEFT else 1
        self.ult = event.source.current_hero.ult
        self.team_num = len([x for x in event.gamestate.teams[event.source.team] if x.state == c.S_ALIVE])
        self.enemy_num = len([x for x in event.gamestate.teams[enemy_team] if x.state == c.S_ALIVE])
        self.value = None
        self.gametime = event.gamestate.gametime
        self.frames = event.gamestate.frames

        if type(event) == EventHeroSwap:
           self.value = event.target.current_hero.name
        if type(event) == EventJoinedTeam:
            self.value = event.source.team
        if type(event) in (EventUltUsed, EventUltGained):
            self.value = event.timer



