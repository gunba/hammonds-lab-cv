from settings import constants as c
from cv.classes.frame_regions import Player
from cv.classes.game_objects import ObjectiveState
import _pickle
import time

class Gamestate(object):
    def __init__(self, url, created):

        # Events (game)
        self.events = list()

        # Teams
        self.teams = dict()
        self.teams[c.TEAM_LEFT] = self.create_team(c.TEAM_LEFT)
        self.teams[c.TEAM_RIGHT] = self.create_team(c.TEAM_RIGHT)

        # For tracking fight numbers, who is alive and dead, ..
        self.death_filter = dict()
        self.resurrect_filter = dict()
        self.matrix_filter = dict()

        # State of the game & objectives
        self.objstate = ObjectiveState()
        self.gametime = 0
        self.deadtime = 0

        # Init vars
        self.ocr_ = True
        self.teamjoin_ = True
        self.creation_time = time.time()

        # Video data (for finding clips)
        self.frames = 0
        self.video = url
        self.created = created

    def instance(self):
        t_inst = _pickle.loads(_pickle.dumps(self, -1))
        t_inst.events = None
        return t_inst

    @staticmethod
    def create_team(team):
        team_list = [Player(0, team), Player(1, team), Player(2, team),
                     Player(3, team), Player(4, team), Player(5, team)]

        return team_list