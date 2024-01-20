# Directories (media)
DIR_MEDIA =         "cv/media"
DIR_HEROES =        "cv/media/heroes/"
DIR_KILLS =         "cv/media/kills/"
DIR_ASSISTS =       "cv/media/assists/"
DIR_ABILITIES =     "cv/media/abilities/"
DIR_MISC =          "cv/media/misc/"
DIR_SMALL_KILLS =   "cv/media/smallkills/"
DIR_SMALL_ASSISTS = "cv/media/smallassists/"
DIR_MATRIX =        "cv/media/matrix/"
DIR_PERCENTAGES =   "cv/media/percentages/"
DIR_REPLAY =        "cv/media/replay/"
DIR_OBJECTIVES =    "cv/media/objectives/"

# Directories (Config)
CONFIG_FILE = "settings/config.ini"
PLAYER_FILE = "settings/players.txt"

# Directories (lab)
LAB_VIDEOS = "video/"
LAB_DEBUG = "video/debug/"
LAB_LOGS = "logs/"
LAB_UPLOAD = "video/upload/"

# Event Types
EVENT_KILL = 'KILL'
EVENT_RESURRECT = 'RESURRECT'
EVENT_DEATH = 'DEATH'
EVENT_SUICIDE = 'SUICIDE'
EVENT_ABILITY = 'ABILITY'
EVENT_ASSIST = 'ASSIST'
EVENT_RESURRECTED = 'RESURRECTED'
EVENT_MATRIX = "MATRIX"
EVENT_MATRIXED = "MATRIXED"

# Team Colors
TEAM_LEFT = 'LEFT'
TEAM_RIGHT = 'RIGHT'
TEAM_DRAW = 'DRAW'

# Player Status
S_ALIVE = "ALIVE"
S_DEAD = "DEAD"
S_RUNBACK = "RUNBACK"

# Team States
TS_ATTACK = "ATTACK"
TS_DEFENSE = "DEFENSE"
TS_ROLLOUT = "ROLLOUT"

# Height & Width Dicts
WIDTH = "WIDTH"
HEIGHT = "HEIGHT"

# Valid Image Models
MOD_BGR = "BGR"
MOD_GRAY = "GRAY"
MOD_QUAD = "QUAD"

# Template Models (Image Splitting)
T_NON_IMAGE = (WIDTH, HEIGHT, MOD_QUAD)

# Frame Response Types
V_VALID = "V_VALID"
V_INVALID = "V_INVALID"
V_PASS = "V_PASS"

# Edge Case Handlers
E_DVA_MECH = "MECH"
E_DVA_BABY = "BABY"

# Killfeed Types
KF_BIG = "BIG"
KF_SMALL = "SMALL"
KF_MATRIX = "matrix"

KF_CONST = dict()
KF_CONST["BIG"] = {"ASSIST_Y1": 9, "ASSIST_Y2": 40, "ASSIST_X1": 7, "ASSIST_X2": 46, "ASSIST_STEP": 19,
                   "ABILITY_Y1": 0, "ABILITY_Y2": 34, "ABILITY_X1": 6, "ABILITY_X2": 29,
                   "LINE_Y1": 7, "LINE_Y2": 41, "LINE_X1": 57, "LINE_X2": 4, "MAX_ATTACK": 30}

KF_CONST["SMALL"]  = {"ASSIST_Y1": 6, "ASSIST_Y2": 25, "ASSIST_X1": 7, "ASSIST_X2": 47, "ASSIST_STEP": 24,
                   "ABILITY_Y1": 0, "ABILITY_Y2": 28,  "ABILITY_X1": 4, "ABILITY_X2": 15,
                   "LINE_Y1": 8, "LINE_Y2": 23, "LINE_X1": 41, "LINE_X2": 3, "MAX_ATTACK": 0}

# Border matching setting - RB for Red Blue, GS for Greyscale
B_BR = "BR"
B_WG = "WG"

# Database credentials
SERVER = 'localhost'
DATABASE = 'gunbaslab'
DRIVER = '{ODBC Driver 17 for SQL Server}'

# Killfeed Buffer Spaces
F_HEROBAR_SLICE_RATIO = 0.43

# Resize ratio for all c.MOD_RESIZE images
RZ_RATIO = 7

# Timers
KF_T_PLAYER_RESPAWN = 10
KF_T_PLAYER_RUNBACK = 6
KF_T_LINE_EXPIRATION = 9

# Default thresholds
TM_MIN_THRESH = 0.05
TM_MAX_THRESH = 999

# Gamestate vars
GS_MIN_EVENTS = 16
GS_MAX_FIGHT_GAP = 20
GS_MAX_BAD_FRAMES = 4

# Color filter
CM_COLOR_THRESH = 40

# Impact Vars
#Result Stat Types
RES_WIN = "WIN"
RES_LOSE = "LOSE"
RES_DRAW = "DRAW"

LAB_GAMEMODE = {
    'HANAMURA': 'ASSAULT',
    'HORIZON LUNAR COLONY': 'ASSAULT',
    'PARIS': 'ASSAULT',
    'TEMPLE OF ANUBIS': 'ASSAULT',
    'VOLSKAYA INDUSTRIES': 'ASSAULT',
    'LIJIANG TOWER': 'CONTROL',
    'NEPAL': 'CONTROL',
    'OASIS': 'CONTROL',
    'BUSAN': 'CONTROL',
    'ILIOS': 'CONTROL',
    'RIALTO': 'ESCORT',
    'JUNKERTOWN': 'ESCORT',
    'DORADO': 'ESCORT',
    'ROUTE 66': 'ESCORT',
    'HAVANA': 'ESCORT',
    'WATCHPOINT GIBRALTAR': 'ESCORT',
    'KINGS ROW': 'HYBRID',
    'EICHENWALDE': 'HYBRID',
    'NUMBANI': 'HYBRID',
    'HOLLYWOOD': 'HYBRID',
    'BLIZZARD WORLD': 'HYBRID'
}

MAP_OBJ = {'A': '1', 'B': '2', 'C': '3', 'LOCKED': '0'}
MAP_SIDE = {TS_ATTACK: '0', TS_DEFENSE: '1', TS_ROLLOUT: '2',
            0: TS_ATTACK, 1: TS_DEFENSE, 2: TS_ROLLOUT}
