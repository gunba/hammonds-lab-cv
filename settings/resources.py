from cv.classes.frame_regions import *
from settings import constants as c

class Resources(object):
    def __init__(self, config):
        # Template Objs (for interchaging with list of actual hero abilities)
        self.A_ATTACK = Match(Ability(c.DIR_ABILITIES + "Attack.png", None), 1, (0, 0))

        # Ult indicator image (for both normal and specced target)
        self.ULT_INDICATORS = list()
        self.ULT_INDICATORS.append(Ultimate(c.DIR_MISC + "SmallIndicator.png"))

        # None Heroes
        self.NONE_LEFT = cv2.imread(c.DIR_MISC + "NoneBlue.png", 0)
        self.NONE_RIGHT = cv2.imread(c.DIR_MISC + "NoneRed.png", 0)
        self.NONE_HERO = {"LEFT": self.NONE_LEFT, "RIGHT": self.NONE_RIGHT}

        # 0% Ult Charge
        self.B_0PCT = cv2.imread(c.DIR_MISC + "B.png", 0)
        self.W_0PCT = cv2.imread(c.DIR_MISC + "W.png", 0)

        self.ZERO_PCT_ULT = dict()
        self.ZERO_PCT_ULT["WG"] = {'LEFT': self.W_0PCT}
        self.ZERO_PCT_ULT["BR"] = {'LEFT': self.B_0PCT}

        # Melee icon
        self.MELEE = Ability(c.DIR_ABILITIES + "Melee.png", None)

        # Ult pct indicators
        self.ULT_PCT = dict()
        for file in os.listdir(c.DIR_PERCENTAGES):
            number = o.get_file_name(file)
            self.ULT_PCT[number] = Number(c.DIR_PERCENTAGES + file)

        # Gamedata Resources
        self.HB_HEROES = dict()

        self.KF_ABILITIES = dict()
        self.KF_KILLS = dict()
        self.KF_UNITS = dict()
        self.KF_ASSISTS = dict()

        self.KF_SMALL_ABILITIES = dict()
        self.KF_SMALL_KILLS = dict()
        self.KF_SMALL_UNITS = dict()
        self.KF_SMALL_ASSISTS = dict()
        self.KF_MATRIX = dict()

        # Build game resources (Heroes, Abilities, Units, etc.)
        for file in os.listdir(c.DIR_HEROES):
            hero_name = o.get_file_name(file)
            p_hero = c.DIR_HEROES + file
            p_assist = c.DIR_ASSISTS + file
            p_small_assist = c.DIR_SMALL_ASSISTS + file
            p_ability = c.DIR_ABILITIES + hero_name + '/'
            p_kill = c.DIR_KILLS + file
            p_unit = c.DIR_KILLS + hero_name + '/'
            p_small_kill = c.DIR_SMALL_KILLS + file
            p_small_unit = c.DIR_SMALL_KILLS + hero_name + '/'
            p_matrix = c.DIR_MATRIX + file

            self.HB_HEROES[hero_name] = Hero(p_hero)
            self.KF_KILLS[hero_name] = Kill(p_kill)
            self.KF_SMALL_KILLS[hero_name] = Kill(p_small_kill)

            if os.path.isfile(p_assist):
                self.KF_ASSISTS[hero_name] = Assist(p_assist)

            if os.path.isfile(p_small_assist):
                self.KF_SMALL_ASSISTS[hero_name] = Assist(p_small_assist)

            if os.path.isfile(p_matrix):
                self.KF_MATRIX[hero_name] = Matrix(p_matrix, hero_name)

            if os.path.isdir(p_unit):
                for subfolder_filename in os.listdir(p_unit):
                    unit_name = o.get_file_name(subfolder_filename)
                    self.KF_UNITS[unit_name] = Unit(p_unit + subfolder_filename, hero_name)

            if os.path.isdir(p_small_unit):
                for subfolder_filename in os.listdir(p_small_unit):
                    unit_name = o.get_file_name(subfolder_filename)
                    self.KF_SMALL_UNITS[unit_name] = Unit(p_small_unit + subfolder_filename, hero_name)

            if os.path.isdir(p_ability):
                for subfolder_filename in os.listdir(p_ability):
                    ability_name = o.get_file_name(subfolder_filename)
                    self.KF_ABILITIES[ability_name] = Ability(p_ability + subfolder_filename, hero_name)
                self.KF_ABILITIES[hero_name + '_Melee'] = Ability(c.DIR_ABILITIES + 'Melee.png', hero_name)


                if os.path.isdir(p_ability):
                    for subfolder_filename in os.listdir(p_ability):
                        ability_name = o.get_file_name(subfolder_filename)
                        self.KF_SMALL_ABILITIES[ability_name] = Ability(p_ability + subfolder_filename, hero_name)
                        self.KF_SMALL_ABILITIES[ability_name].image = self.KF_SMALL_ABILITIES[ability_name].image_small
                    self.KF_SMALL_ABILITIES[hero_name + '_Melee'] = Ability(c.DIR_ABILITIES + 'Melee.png', hero_name)
                    self.KF_SMALL_ABILITIES[hero_name + '_Melee'].image = self.KF_SMALL_ABILITIES[hero_name + '_Melee'].image_small
                    self.KF_SMALL_ABILITIES[hero_name + '_Attack'] = Ability(c.DIR_ABILITIES + "Attack.png", hero_name)

                self.OBJ_KOTH_CAPPED_LEFT = list()
                self.OBJ_KOTH_CAPPED_RIGHT = list()
                self.OBJ_KOTH_NOT_CAPPED = list()
                self.OBJ_ROUND_SCORE_LEFT = list()
                self.OBJ_ROUND_SCORE_RIGHT = list()

        self.DIR_OBJECTIVES = c.DIR_OBJECTIVES + config.UI_FONT + "/"
        self.DIR_OBJ_KOTH_CAPPED_LEFT = "KOTH_CAPPED_LEFT_" + config.UI_COLOR_MATCHING
        self.DIR_OBJ_KOTH_CAPPED_RIGHT = "KOTH_CAPPED_RIGHT_" + config.UI_COLOR_MATCHING
        self.DIR_OBJ_ROUND_SCORE_LEFT = "ROUND_SCORE_LEFT_" + config.UI_COLOR_MATCHING
        self.DIR_OBJ_ROUND_SCORE_RIGHT = "ROUND_SCORE_RIGHT_" + config.UI_COLOR_MATCHING
        self.DIR_OBJ_KOTH_NOT_CAPPED = "KOTH_NOT_CAPPED/"

        # Build game resources (objectives)
        for file in os.listdir(self.DIR_OBJECTIVES + self.DIR_OBJ_ROUND_SCORE_LEFT):
            self.OBJ_ROUND_SCORE_LEFT.append(Objective(self.DIR_OBJECTIVES + self.DIR_OBJ_ROUND_SCORE_LEFT + "/" + file))

        for file in os.listdir(self.DIR_OBJECTIVES + self.DIR_OBJ_ROUND_SCORE_RIGHT):
            self.OBJ_ROUND_SCORE_RIGHT.append(Objective(self.DIR_OBJECTIVES + self.DIR_OBJ_ROUND_SCORE_RIGHT + "/" + file))

        for file in os.listdir(self.DIR_OBJECTIVES + self.DIR_OBJ_KOTH_CAPPED_LEFT):
            self.OBJ_KOTH_CAPPED_LEFT.append(Objective(self.DIR_OBJECTIVES + self.DIR_OBJ_KOTH_CAPPED_LEFT + "/" + file))

        for file in os.listdir(self.DIR_OBJECTIVES + self.DIR_OBJ_KOTH_CAPPED_RIGHT):
            self.OBJ_KOTH_CAPPED_RIGHT.append(Objective(self.DIR_OBJECTIVES + self.DIR_OBJ_KOTH_CAPPED_RIGHT + "/" + file))

        for file in os.listdir(self.DIR_OBJECTIVES + self.DIR_OBJ_KOTH_NOT_CAPPED):
            self.OBJ_KOTH_NOT_CAPPED.append(Objective(self.DIR_OBJECTIVES + self.DIR_OBJ_KOTH_NOT_CAPPED + file))





