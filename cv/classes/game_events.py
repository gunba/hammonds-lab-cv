from settings import constants as c
from cv.workflow import image_functions as a
import cv2

class EventUltGained(object):
    def __init__(self, source, timer, gamestate):
        self.source = source.instance()
        self.gamestate = gamestate.instance()
        self.timer = timer

class EventUltUsed(EventUltGained):
    pass

class EventJoinedTeam(object):
    def __init__(self, source, gamestate):
        # This event is important - we store the original OCR detected for
        # the player in this event and prevent it from being stored elsewhere
        self.source = source.instance()
        source.name_ocr = None
        self.gamestate = gamestate.instance()

class EventHeroSwap(object):
    def __init__(self, source, target, gamestate):
        self.source = source.instance()
        self.target = target.instance()
        self.gamestate = gamestate.instance()

class EventResurrect(object):
    def __init__(self, line, gamestate):
        self.source = line[0].player.instance()
        self.ability = line[1].entity
        self.target = line[2].player.instance()
        self.assists = list()
        self.gamestate = gamestate.instance()

class EventKill(object):
    def __init__(self, line, gamestate):
        # Kills are a bit involved unfortunately
        def get_next_event(line, type, if_none=None):
            return next((x for x in line if x.type == type), if_none)

        kill_event = get_next_event(line, c.EVENT_KILL)
        death_event = get_next_event(line, c.EVENT_DEATH)
        ability_event = get_next_event(line, c.EVENT_ABILITY)

        assist_events = (x for x in line if x.type == c.EVENT_ASSIST)

        assists = list()
        for assist in assist_events:
            assists.append(assist.player.instance())

        self.source = kill_event.player.instance()
        self.target = death_event.player.instance()
        self.ability = ability_event.entity
        self.entity = death_event.entity
        self.assists = assists
        self.gamestate = gamestate.instance()

class EventMatrix(object):
    def __init__(self, line, gamestate):
        self.source = line[0].player.instance()
        self.ability = line[1].entity
        self.target = line[2].player.instance()
        self.assists = list()
        self.gamestate = gamestate.instance()

class EventFightStart(object):
    def __init__(self, gamestate):
        self.gamestate = gamestate.instance()

class EventFightEnd(object):
    def __init__(self, tpl):
        self.result = tpl[0]
        self.gamestate = tpl[1].instance()

class EventMapLoaded(object):
    def __init__(self, map, gamestate):
        #Save frame as a medium quality jpg (so user can decide map later)
        self.map = a.numpy_to_jpg(cv2.cvtColor(map, cv2.COLOR_BGR2RGB))
        self.left_team = c.TEAM_LEFT
        self.right_team = c.TEAM_RIGHT
        self.region = None
        self.patch = None
        self.gamestate = gamestate.instance()
        self.video = gamestate.video
        self.created = gamestate.created





