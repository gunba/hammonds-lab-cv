from settings import constants as c
from settings.timeit import timeit
import pandas as pd
import pyodbc
import numpy as np


def create_cursor():
    conn = pyodbc.connect('DRIVER=%s;SERVER=%s;Trusted_Connection=yes;' % (c.DRIVER, c.SERVER), database=c.DATABASE)
    return conn, conn.cursor()

@timeit
def preload():
    conn, cursor = create_cursor()

    _defaults = defaults()

    _dbfights = pd.read_sql_query("SELECT * FROM gen_fights", conn)
    _dbcomps = pd.read_sql_query("SELECT * FROM gen_comps", conn)

    _fights = build_fights(_dbfights)
    _perf = build_perf(_fights.copy())
    _comps = build_comps(_dbcomps, _defaults['selects'])
    _maps = build_maps(_comps.copy(), _defaults['selects'])
    _games = build_games(_maps.copy())
    conn.close()

    return {'fights': _fights,
        'comps': _comps,
        'perf': _perf,
        'maps': _maps,
        'games': _games}

def defaults():
    conn, cursor = create_cursor()

    #Minimum date of stored data
    timeit(cursor.execute("SELECT min(created) created FROM gen_fights"))
    _mindate = str(cursor.fetchone()[0]).split(" ")[0]

    #Maximum date of stored data
    timeit(cursor.execute("SELECT max(created) FROM gen_fights"))
    _maxdate = str(cursor.fetchone()[0]).split(" ")[0]

    #Valid fields for dropdowns (heroes, etc.)
    cursor.execute("SELECT * FROM gen_defaults",)
    _defaults = [x for x in cursor.fetchall()]
    _defaults.sort(key=lambda x: x.val)

    #Valid fields for dropdowns (heroes, etc.)
    cursor.execute("SELECT * FROM selects",)
    _selects = [x for x in cursor.fetchall()]
    _selects.sort(key=lambda x: x.key)
    conn.close()

    return {
        'defaults': _defaults,
        'selects': _selects,
        'mindate': _mindate,
        'maxdate': _maxdate
    }

@timeit
def build_fights(sql):
    return sql

@timeit
def build_comps(tbl, selects):

    def nonvec_ot(row):
        _mode = [x[1] for x in selects if x[0] == row['map']][0]
        if _mode == 'CONTROL':
            return row.objective
        if _mode in ('HYBRID', 'ESCORT'):
            return 1 + ((row.objective-1)%3)
        else:
            return 1 + ((row.objective - 1) % 2)

    tbl['usar'] = tbl.result & tbl.ults > 0
    tbl['ubool'] = tbl.ults > 0
    tbl['fkgtfd'] = tbl.fk > tbl.fd
    tbl['fkltfd'] = tbl.fk < tbl.fd
    tbl['rafkgtfd'] = tbl.result & tbl.fkgtfd
    tbl['rafkltfd'] = tbl.result & tbl.fkltfd
    tbl['kpadk'] = (tbl.kills + tbl.assists) / tbl.kills

    tbl.objective = tbl.apply(nonvec_ot, axis=1)
    return tbl

@timeit
def build_perf(tbl):
    _tbl = tbl

    _tbl['i'] = (np.where(_tbl.kills > 0, (_tbl.kills - (_tbl.assisted * 0.15)) * (2 ** (-2 - _tbl.kpos)), 0) +
                 np.where(_tbl.assists > 0, ((_tbl.assists * (2 ** (-2 - _tbl.apos))) * 0.15), 0)) - \
                np.where(_tbl.deaths > 0, (_tbl.deaths * (2 ** (-2 - _tbl.dpos))), 0)
    _tbl['ewu'] = np.where(_tbl.ultdiff >= 0, 1 - 2 ** (-1 - _tbl.ultdiff), 2 ** (-1 + _tbl.ultdiff))
    _tbl['iw'] = _tbl.i * _tbl.result
    _tbl['il'] = _tbl.i * (1 - _tbl.result)
    _tbl['ue'] = ((1 - _tbl.ewu) * _tbl.result) * 1
    _tbl['uew'] = _tbl.ue * _tbl.result
    _tbl['uel'] = _tbl.ue * (1 - _tbl.result)

    #Saved vectors (optimizing)
    _tbl['pfxr'] = _tbl.pf * _tbl.result
    _tbl['pfnxr'] = _tbl.pf * (1 - _tbl.result)
    _tbl['rafk'] = _tbl.result & _tbl.fk > 0
    _tbl['rafd'] = _tbl.result & _tbl.fd > 0
    _tbl['rafa'] = _tbl.result & _tbl.fa > 0
    _tbl['fkbool'] = _tbl.fk > 0
    _tbl['fdbool'] = _tbl.fd > 0
    _tbl['fabool'] = _tbl.fa > 0
    _tbl['usar'] = _tbl.result & _tbl.ults > 0
    _tbl['uuar'] = _tbl.result & _tbl.ultsunique > 0
    _tbl['umar'] = _tbl.result & (_tbl.ultsunique == 0)
    _tbl['ubool'] = _tbl.ults > 0
    _tbl['uubool'] = _tbl.ultsunique > 0
    _tbl['umbool'] = _tbl.ultsunique == 0

    return _tbl


@timeit
def build_maps(tbl, sel):
    def nonvec_mode(row): return [x[1] for x in sel if x[0] == row['map']][0]
    _tbl = tbl.groupby(['map', 'objective', 'side', 'id_teamenemy', 'round'])\
        .apply(lambda x: pd.Series({
            'player_team': x.player_team.iat[0],
            'enemy_team': x.enemy_team.iat[0],
            'fw': x.result.sum(),
            'tp': x.tp.sum(),
            'f': x.result.count(),
            'created': x.created.iat[0],
            'patch': x.patch.iat[0],
            'region': x.region.iat[0],
            'id_enemyteam': x.id_enemyteam.iat[0],
            'start': x.start.iat[0],
            'prog': x.prog.iat[0]
    })).reset_index()

    _tbl['mode'] = _tbl.apply(nonvec_mode, axis=1)

    #Saved vectors (optimizing)
    _tbl['fwxob1si0'] = _tbl.fw * ((_tbl.objective == 1) & (_tbl.side == 0))
    _tbl['fwxob2si0'] = _tbl.fw * ((_tbl.objective == 2) & (_tbl.side == 0))
    _tbl['fwxob3si0'] = _tbl.fw * ((_tbl.objective == 3) & (_tbl.side == 0))
    _tbl['fxob1si0'] = _tbl.f * ((_tbl.objective == 1) & (_tbl.side == 0))
    _tbl['fxob2si0'] = _tbl.f * ((_tbl.objective == 2) & (_tbl.side == 0))
    _tbl['fxob3si0'] = _tbl.f * ((_tbl.objective == 3) & (_tbl.side == 0))
    _tbl['fwxob1si1'] = _tbl.fw * ((_tbl.objective == 1) & (_tbl.side == 1))
    _tbl['fwxob2si1'] = _tbl.fw * ((_tbl.objective == 2) & (_tbl.side == 1))
    _tbl['fwxob3si1'] = _tbl.fw * ((_tbl.objective == 3) & (_tbl.side == 1))
    _tbl['fxob1si1'] = _tbl.f * ((_tbl.objective == 1) & (_tbl.side == 1))
    _tbl['fxob2si1'] = _tbl.f * ((_tbl.objective == 2) & (_tbl.side == 1))
    _tbl['fxob3si1'] = _tbl.f * ((_tbl.objective == 3) & (_tbl.side == 1))
    _tbl['fxob1'] = _tbl.f * (_tbl.objective == 1)
    _tbl['fxob2'] = _tbl.f * (_tbl.objective == 2)
    _tbl['fxob3'] = _tbl.f * (_tbl.objective == 3)
    _tbl['fwxob1'] = _tbl.fw * (_tbl.objective == 1)
    _tbl['fwxob2'] = _tbl.fw * (_tbl.objective == 2)
    _tbl['fwxob3'] = _tbl.fw * (_tbl.objective == 3)
    _tbl['fwxsi0'] = _tbl.fw * (_tbl.side == 0)
    _tbl['fwxsi1'] = _tbl.fw * (_tbl.side == 1)
    _tbl['fwxsi2'] = _tbl.fw * (_tbl.side == 2)
    _tbl['fxsi0'] = _tbl.f * (_tbl.side == 0)
    _tbl['fxsi1'] = _tbl.f * (_tbl.side == 1)
    _tbl['fxsi2'] = _tbl.f * (_tbl.side == 2)
    return _tbl

@timeit
def build_games(tbl):

    def nonvec_teamsort(row):
        sorter = [row.player_team, row.enemy_team]
        sorter.sort()
        return sorter[0] + sorter[1]

    tbl['teamsort'] = tbl.apply(nonvec_teamsort, axis=1)
    tbl['teamunsort'] = tbl.player_team + tbl.enemy_team

    _tbl = tbl[tbl.teamsort == tbl.teamunsort]

    _tbl = _tbl.groupby(['id_teamenemy'])\
        .apply(lambda x: pd.Series({
            #'id_teamenemy': x.id_teamenemy.iloc[0],
            'id_enemyteam': x.id_enemyteam.iat[0],
            'teaml': x.player_team.iat[0],
            'teamr': x.enemy_team.iat[0],
            't': x.tp.sum(),
            'fwl': x.fw.sum() / x.f.sum(),
            'fwr': 1 - x.fw.sum() / x.f.sum(),
            'maps': ','.join(sorted(x.map.unique()[:min(5, len(x.map.unique()))])),
            'patch': x.patch.iat[0],
            'region': x.region.iat[0],
            'created': x.created.iat[0]
    })).reset_index()

    return _tbl

