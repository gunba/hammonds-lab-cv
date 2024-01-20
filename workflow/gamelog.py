import pyodbc
from settings import constants as c
from settings.timeit import timeit
from recordclass import recordclass
from workflow import decorator as d

entry = recordclass('entry', 'text, flavor, nums, time, vod, side')
header = recordclass('header', 'text, winner, kills, ults, vod')
events = recordclass('events', 'rows, assists, rounds, kills, ults')

def create_cursor():
    conn = pyodbc.connect('DRIVER=%s;SERVER=%s;Trusted_Connection=yes;' % (c.DRIVER, c.SERVER), database=c.DATABASE)
    return conn, conn.cursor()

@timeit
def log(fights):
    _events = get_events(fights)
    _e = sort_events(_events)
    _decor = decorator(_e)

    return _decor

def sort_events(_events):
    _e = events(rows={}, assists={}, rounds={}, kills={}, ults={})

    for k in _events['k']:
        _e.assists[k.id] = [x for x in _events['a'] if x.event == k.id]

    for f in _events['f']:
        _e.rounds[f.id] = next(x for x in _events['r'] if x.id == f.round)

    for f in _events['f']:
        e = [x for x in _events['k'] + _events['h'] if x.fight == f.id]
        e.sort(key=lambda x: x.gametime)
        _e.kills[f.id] = sum([1 for x in e if x.type.strip() == 'EventKill' and x.left_team]), sum([1 for x in e if x.type.strip() == 'EventKill' and not x.left_team])
        _e.ults[f.id] = sum([1 for x in e if x.type.strip() == 'EventUltUsed' and x.team]), sum([1 for x in e if x.type.strip() == 'EventUltUsed' and not x.team])
        _e.rows[f.id] = [f] + e

    return _e

def decorator(eve):
    _decor = {}
    for f, v in eve.rows.items():
        _fight = v[0]
        _events = [decorate(_fight, eve)]

        for e in v[1:]:
            _events.append(decorate(e, eve, _fight))

        _decor[f] = _events

    return _decor


def decorate(row, e, fight=None):
    _assists = e.assists[row.id] if row.id in e.assists else None

    _colors = {
        0: 'deepskyblue',
        1: 'indianred',
        2: '#FFFFFF'
    }

    _types = {
        'EventUltUsed': lambda x, y, r: entry(text="%s %s used their ultimate %s" % (d.heroify(x.hero), d.boldify(x.name), d.abilify(x.hero)),
                                    flavor="UHT %ss" % x.value.strip(),
                                    nums= "%s vs %s" % (d.colorify(x.right_num if x.team else x.left_num, _colors[y.right_side]), d.colorify(x.left_num if x.team else x.right_num, _colors[y.left_side])),
                                    time='+%s' % (x.gametime - y.first),
                                    vod=d.vodify(vod_link(r.video, x.frames)),
                                    side=c.MAP_SIDE[y.right_side if x.team else y.left_side]),

        'EventUltGained': lambda x, y, r: entry(text="%s %s's ultimate is now online %s" % (d.heroify(x.hero), d.boldify(x.name), d.abilify(x.hero)),
                                    flavor="UGT %ss" % x.value.strip(),
                                    nums= "%s vs %s" % (d.colorify(x.right_num if x.team else x.left_num, _colors[y.right_side]), d.colorify(x.left_num if x.team else x.right_num, _colors[y.left_side])),
                                    time='+%s' % (x.gametime - y.first),
                                    vod=d.vodify(vod_link(r.video, x.frames)),
                                    side=c.MAP_SIDE[y.right_side if x.team else y.left_side]),

        'EventResurrect': lambda x, y, r: entry(text="%s %s resurrected %s %s %s" % (d.heroify(x.left_hero), d.boldify(x.left_name), d.abilify(x.ability), d.heroify(x.right_hero), d.boldify(x.right_name)),
                                    flavor="",
                                    nums= "%s vs %s" % (d.colorify(x.right_num if x.left_team else x.left_num, _colors[y.right_side]), d.colorify(x.left_num if x.left_team else x.right_num, _colors[y.left_side])),
                                    time='+%s' % (x.gametime - y.first),
                                    vod=d.vodify(vod_link(r.video, x.frames)),
                                    side=c.MAP_SIDE[y.right_side if x.left_team else y.left_side]),

        'EventMatrix': lambda x, y, r: entry(text="%s %s matrixed %s's %s ultimate" % (d.heroify(x.left_hero), d.boldify(x.left_name), d.heroify(x.right_hero), d.boldify(x.right_name)),
                                    flavor="",
                                    nums= "%s vs %s" % (d.colorify(x.right_num if x.left_team else x.left_num, _colors[y.right_side]), d.colorify(x.left_num if x.left_team else x.right_num, _colors[y.left_side])),
                                    time='+%s' % (x.gametime - y.first),
                                    vod=d.vodify(vod_link(r.video, x.frames)),
                                    side=c.MAP_SIDE[y.right_side if x.left_team else y.left_side]),

        'EventHeroSwap': lambda x, y, r: entry(text="%s %s has swapped heroes → %s" % (d.heroify(x.value), d.boldify(x.name), d.heroify(x.hero)),
                                    flavor="",
                                    nums= "%s vs %s" % (d.colorify(x.right_num if x.team else x.left_num, _colors[y.right_side]), d.colorify(x.left_num if x.team else x.right_num, _colors[y.left_side])),
                                    time='+%s' % (x.gametime - y.first),
                                    vod=d.vodify(vod_link(r.video, x.frames)),
                                    side=c.MAP_SIDE[y.right_side if x.team else y.left_side]),

        'EventKill': lambda x, y, r: entry(text="%s %s %s %s %s %s" % (d.heroify(x.left_hero), d.boldify(x.left_name), 'eliminated' if x.right_hero == x.entity else 'destroyed', d.abilify(x.ability), d.heroify(x.entity), d.boldify(x.right_name)),
                                    flavor=("%s" % "".join([d.heroify(a.hero) for a in _assists])) if _assists else "",
                                    nums= "%s vs %s" % (d.colorify(x.right_num if x.left_team else x.left_num, _colors[y.right_side]), d.colorify(x.left_num if x.left_team else x.right_num, _colors[y.left_side])),
                                    time='+%s' % (x.gametime - y.first),
                                    vod=d.vodify(vod_link(r.video, x.frames)),
                                    side=c.MAP_SIDE[y.right_side if x.left_team else y.left_side]),

        'EventFight': lambda x, r: header(text="%s %s   %s %s (PT %s)" % (d.teamify(r.left_team), c.MAP_SIDE[x.left_side], d.teamify(r.right_team), c.MAP_SIDE[x.right_side], x.objective),
                                    winner="WINNER: %s" % (d.teamify(r.right_team) if x.winner else d.teamify(r.left_team)),
                                    vod=d.vodify(vod_link(r.video, x.frames)),
                                    ults=" %s vs %s" % (e.ults[x.id][1], e.ults[x.id][0]),
                                    kills=" %s vs %s" % (e.kills[x.id][1], e.kills[x.id][0]))
    }
    #text, winner, kills, ults, vod
    if hasattr(row, 'type'):
        return _types[row.type.strip()](row, fight, e.rounds[row.fight])
    else:
        return _types['EventFight'](row, e.rounds[row.id])

#TODO: Make generic
def vod_link(url, frames):
    return ("%s?t=%s%s" % (url if 'twitch' in url else url, frames, "s" if 'twitch' in url else "")) if frames else ""

def get_events(fights):
    conn, cursor = create_cursor()

    _fights = "".join(str(fights))

    _query = "SELECT * FROM KILLFEED_EVENTS WHERE FIGHT IN (%s)" % _fights[1:-1]
    print(_query)
    cursor.execute(_query)
    _killfeed = [x for x in cursor.fetchall()]

    _query = "SELECT * FROM HEROBAR_EVENTS WHERE FIGHT IN (%s)" % _fights[1:-1]
    cursor.execute(_query)
    _herobar = [x for x in cursor.fetchall()]

    _query = "SELECT * FROM FIGHTS WHERE ID IN (%s)" % _fights[1:-1]
    cursor.execute(_query)
    _fights = [x for x in cursor.fetchall()]

    _round_id = "".join(str([x.round for x in _fights]))
    _query = "SELECT * FROM ROUNDS WHERE ID IN (%s)" % _round_id[1:-1]
    cursor.execute(_query)
    _rounds = [x for x in cursor.fetchall()]

    _killfeed_id = "".join(str([x.id for x in _killfeed]))
    _query = "SELECT * FROM ASSISTS WHERE EVENT IN (%s)" % _killfeed_id[1:-1]
    cursor.execute(_query)
    _assists = [x for x in cursor.fetchall()]

    _events = {'k': _killfeed, 'h': _herobar, 'f': _fights, 'a': _assists, 'r': _rounds}

    conn.close()
    return _events