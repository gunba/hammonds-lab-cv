import math
import os
import datetime

# Table field text decorators
def multi_heroify(x, foo='table-inline-comp', _inner =''):
    return '<span class="%s">%s</span>' % (foo, ''.join([heroify(y, foo) for y in x.split(' ')]))

def colorify(x, clr):
    return '<span style="color:%s">%s</span>' % (clr, x)

def heroify(x, cls='table-inline-comp'):
    return '<div class="sort-string-hack">%s</div><img src="/static/ow/heroes/%s.png" value="%s" class="%s" alt="%s">' % (x.lower().strip(), x.lower().strip(), x.lower().strip(), cls, x.lower().strip())

def multi_mapify(x, cls='table-inline-map', _inner =''):
    return '<span class="%s">%s</span>' % (cls, ''.join([mapify(y, cls) for y in x.split(',')]))

def mapify(x, cls='table-inline-map'):
    return '<div class="sort-string-hack">%s</div><img src="/static/ow/maps/%s.jpg" value="%s" class="%s">' % (x.strip(), x.strip(), x.strip(), cls)

def percentify(x):
    return str(int(x*100)) + "%" if not math.isnan(x) and not math.isinf(x) else ''

def conditionify(x):
    return '<span style="color:%s">%s%%</span>' % (condition(x), (str(int(round(x * 100 if not math.isnan(x) else -1, 0)))))

def condition(percent):
    return '#1d1d1d' if math.isnan(percent) else '#%02x%02x%02x' % (int(0 + ((255 - 0) *  min(200 - ((percent*100) * 2), 100) / 100.0)), int(0 + ((255 - 0) * min((percent*100) * 2, 100) / 100.0)), 0)

def intify(x):
    return str(int(x)) if not (math.isnan(x) or isinstance(x, str)) else ''

def boldify(x):
    return '<b>%s</b>' % x

def timeify(x):
    return str(datetime.timedelta(seconds=int(x)))

def dateify(x):
    return str(x.date())

def teamify(x, small=True):
    return ('<div class="sort-string-hack">%s</div><img src="/static/ow/teams/%s.png" class="team-logo-small">' % (x, x) if os.path.exists("static/ow/teams/%s.png" % x) else ''.join(e[0] for e in x.split())) if small else (('<img src="/static/ow/teams/%s.png" class="team-logo-big">' % x if os.path.exists("static/ow/teams/%s.png" % x) else '') + x)

def vodify(x):
    if not x:
        return ''
    elif 'youtu.be' in x:
        return '<a target="_blank" href=%s><i style="color: #cc181e;" class="fab fa-youtube"></i></a>' % x
    elif 'twitch.tv' in x:
        return '<a target="_blank" href=%s><i style="color: #6441a5;" class="fab fa-twitch"></i></a>' % x

def abilify(x, cls='table-inline-ability'):
    return '<img src="/static/ow/abilities/%s.png" value="%s" class="%s" alt="%s">' % (x.strip(), x.strip(), cls, x.strip())

def applymap(lst):
    _lamb = {}

    for x in lst:
        if x in _applies:
            _lamb[x] =  _applies[x]

    return _lamb

def applypandas(tbl):
    for x in tbl:
        if x in _applies:
            tbl[x] = tbl[x].apply(_applies[x])

    return tbl

_applies = {
    'fw': lambda x: conditionify(x),
    'fk%': lambda x: percentify(x),
    'fd%': lambda x: percentify(x),
    'fa%': lambda x: percentify(x),
    'fkw': lambda x: percentify(x),
    'fdw': lambda x: percentify(x),
    'faw': lambda x: percentify(x),
    'ufw': lambda x: percentify(x),
    'kpa': lambda x: percentify(x),
    'ku': lambda x: percentify(x),
    'du': lambda x: percentify(x),
    'au': lambda x: percentify(x),
    'kt': lambda x: intify(x),
    'dt': lambda x: intify(x),
    'at': lambda x: intify(x),
    'uht': lambda x: intify(x),
    'ugt': lambda x: intify(x),
    'uut': lambda x: intify(x),
    'hero': lambda x: heroify(x),
    'i': lambda x: percentify(x),
    'i50': lambda x: percentify(x),
    'ue': lambda x: percentify(x),
    'u50': lambda x: percentify(x),
    'ip': lambda x: conditionify(x),
    'up': lambda x: conditionify(x),
    'um': lambda x: percentify(x),
    'uu': lambda x: percentify(x),
    'arw': lambda x: conditionify(x),
    'f': lambda x: intify(x),
    'upw': lambda x: percentify(x),
    'comp': lambda x: multi_heroify(x),
    'atk': lambda x: percentify(x),
    'saw': lambda x: percentify(x),
    'sdw': lambda x: percentify(x),
    'aw1': lambda x: percentify(x),
    'aw2': lambda x: percentify(x),
    'aw3': lambda x: percentify(x),
    'dw1': lambda x: percentify(x),
    'dw2': lambda x: percentify(x),
    'dw3': lambda x: percentify(x),
    't': lambda x: timeify(x),
    'fw1': lambda x: percentify(x),
    'fw2': lambda x: percentify(x),
    'fw3': lambda x: percentify(x),
    'f1': lambda x: intify(x),
    'f2': lambda x: intify(x),
    'f3': lambda x: intify(x),
    'flen': lambda x: intify(x),
    'fwl': lambda x: conditionify(x),
    'fwr': lambda x: conditionify(x),
    'maps': lambda x: multi_mapify(x),
    'team': lambda x: teamify(x),
    'teamr': lambda x: teamify(x, small=False),
    'teaml': lambda x: teamify(x, small=False),
    'aw': lambda x: percentify(x),
    'dw': lambda x: percentify(x),
    'created': lambda x: dateify(x),
    'rlw': lambda x: percentify(x),
    'fwm': lambda x: percentify(x),
    'mat': lambda x: percentify(x)
}