import _pickle

import settings.constants as c

class Player(object):
    def __init__(self, slot = None, team = None, current_hero = None, name = ''):
        self.slot = slot
        self.name = name
        self.name_ocr = None
        self.team = team
        self.state = c.S_ALIVE
        self.death_allowed = False

        self.current_hero = current_hero
        self.swap_primer = current_hero


    def instance(self):
        return _pickle.loads(_pickle.dumps(self, -1))


class GameAbility(object):
    def __init__(self, name):
        self.name = name


class GameHero(object):
    def __init__(self, name):
        # For finding the hero in images, etc.
        self.name = name
        self.ult = False
        self.ult_pct = -1

    def instance(self):
        return _pickle.loads(_pickle.dumps(self, -1))


class GameUnit(object):
    def __init__(self, name):
        self.name = name

class GameMatrix(object):
    def __init__(self, name):
        self.name = name

class ObjectiveState(object):
    def __init__(self):
        self.round = "UNSET"
        self.left_state = "UNSET"
        self.right_state = "UNSET"
        self.valid = False

