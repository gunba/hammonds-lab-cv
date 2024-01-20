import configparser
from settings import constants as c

cp = configparser.ConfigParser()
cp.read(c.CONFIG_FILE)

def get_config(config_key):
    config = cp[config_key]
    return Config(config)

class Config(object):
    def __init__(self, config):

        # Thresholds (TM)
        self.TM_THRESH_OBJ = float(config["CV_TM_THRESH_OBJ"])
        self.TM_THRESH_ULT = float(config["CV_TM_THRESH_ULT"])
        self.TM_THRESH_ZERO_ULT = float(config["CV_TM_THRESH_ZERO_ULT"])
        self.TM_THRESH_ASSIST = float(config["CV_TM_THRESH_ASSIST"])
        self.TM_THRESH_HEROBAR = float(config["CV_TM_THRESH_HEROBAR"])
        self.TM_THRESH_KILL = float(config["CV_TM_THRESH_KILL"])
        self.TM_THRESH_NONEHERO = float(config["CV_TM_THRESH_NONEHERO"])
        self.TM_THRESH_REPLAY = float(config["CV_TM_THRESH_REPLAY"])
        self.TM_THRESH_SMALL_KILL = float(config["CV_TM_THRESH_SMALL_KILL"])
        self.TM_THRESH_ULT_NUM = float(config["CV_TM_THRESH_ULT_NUM"])

        # UI Elements according to config (Live, OWL, etc.)
        self.UI_HEROBAR = {'LEFT_X1': int(config['UI_HEROBAR_LEFT_X1']), 'LEFT_X2': int(config['UI_HEROBAR_LEFT_X2']),
                      'RIGHT_X1': int(config['UI_HEROBAR_RIGHT_X1']),
                      'RIGHT_X2': int(config['UI_HEROBAR_RIGHT_X2']),
                      'Y1': int(config['UI_HEROBAR_Y1']), 'Y2': int(config['UI_HEROBAR_Y2'])}

        self.UI_KILLFEED = {'X1': int(config['UI_KILLFEED_X1']), 'X2': int(config['UI_KILLFEED_X2']),
                       'Y1': int(config['UI_KILLFEED_Y1']), 'Y2': int(config['UI_KILLFEED_Y2']), 'SMALL': int(config['UI_KILLFEED_SMALL'])}

        self.UI_NAMEBOX = {'LEFT_X1': int(config['UI_NAMEBOX_LEFT_X1']), 'LEFT_X2': int(config['UI_NAMEBOX_LEFT_X2']),
                      'RIGHT_X1': int(config['UI_NAMEBOX_RIGHT_X1']),
                      'RIGHT_X2': int(config['UI_NAMEBOX_RIGHT_X2']),
                      'Y1': int(config['UI_NAMEBOX_Y1']), 'Y2': int(config['UI_NAMEBOX_Y2'])}

        self.UI_OBJ = {"X1": int(config['UI_OBJ_X1']), "X2": int(config['UI_OBJ_X2']),
                  "XM": int(config['UI_OBJ_XM']),
                  "Y1": int(config['UI_OBJ_Y1']), "Y2": int(config['UI_OBJ_Y2']),
                  "CENTER_X1": int(config['UI_OBJ_CENTER_X1']), "CENTER_X2": int(config['UI_OBJ_CENTER_X2']),
                  "CENTER_Y1": int(config['UI_OBJ_CENTER_Y1']), "CENTER_Y2": int(config['UI_OBJ_CENTER_Y2'])}

        # Get UI general settings - Border matching, font for OCR, UI language for objs.
        self.UI_COLOR_MATCHING = config['UI_COLOR_MATCHING']
        self.UI_FONT = config['UI_FONT']
