from datetime import timedelta
from dateutil import parser
import numpy as np
import pandas as pd
from flask import session
from settings.timeit import timeit
import workflow.groupby as gb
from workflow import gamelog as gl

pd.set_option("display.max_columns", 999)
pd.set_option("display.max_rows", 999)
pd.set_option('display.max_colwidth', -1)
pd.set_option('mode.chained_assignment', None)
pd.set_option('precision', 5)
pd.set_option('compute.use_numexpr', True)

_prequeries = {
    'mindate': (lambda x: "created >= '%s'" % str((parser.parse(x)-timedelta(days=1)).strftime('%Y-%m-%d')), 'created'),
    'maxdate': (lambda x: "& created <= '%s'" % str((parser.parse(x)+timedelta(days=1)).strftime('%Y-%m-%d')), 'created'),
    'team': (lambda x: "& player_team == '%s'" % x, 'player_team'),
    'hero': (lambda x: "& hero == '%s'" % x, 'hero'),
    'patch': (lambda x: "& patch == '%s'" % x, 'patch'),
    'region': (lambda x: "& region == '%s'" % x, 'region'),
    'map': (lambda x: "& map == '%s'" % x if x != 'ALL' else '', 'map'),
    'objective': (lambda x: "& objective == %i" % int(x), 'objective'),
    'side': (lambda x: "& side == %i" % int(x), 'side')
}

_postqueries = {
    'timeplayed': (lambda x: 't>%i' % int(x), 't'),
    'hero_filter': (lambda x: "comp.str.contains('%s')" % x.strip(), 'comp')
}

@timeit
def prequery(tbl, params, excludes=None):
    if excludes is None:
        excludes = []

    _query = ''

    #Ordered this way to guarantee OOP.
    for key, value in _prequeries.items():
        if key in params and key not in excludes and value[1] in tbl:
            _query += value[0](params[key])

    return tbl.query(_query) if _query else tbl


@timeit
def postquery(tbl, params, excludes=None):
    if excludes is None:
        excludes = []

    for key, value in params.items():
        if key in _postqueries and key not in excludes and _postqueries[key][1] in tbl:
            tbl = tbl.query(_postqueries[key][0](value))

    return tbl

@timeit
def fights(tbl, params):
    _tbl = prequery(tbl, params)

    if not _tbl.empty:
        _tbl = gb.fights(_tbl, ['hero', 'name', 'player_team'])

        _tbl = postquery(_tbl, params)

        _tbl.insert(5, 'ip', _tbl.groupby('hero').i50.rank("dense", pct=True))
        _tbl.insert(7, 'up', _tbl.groupby('hero').u50.rank("dense", pct=True))
    else:
        _tbl = None
    return _tbl

@timeit
def comps(tbl, params):
    _tbl = prequery(tbl, params)

    def nonvec_rw(row):
        _rounds = tbl[(tbl.comp == row.comp)][['id_teamround']] #List of rounds + teams with the comp played.
        _rows = np.where(np.logical_and(tbl.id_teamround.isin(_rounds.id_teamround), tbl.comp != row.comp))
        _rows = tbl['result'].iloc[_rows]
        return _rows.sum() / _rows.count()

    if not _tbl.empty:
        _tbl = gb.comps(_tbl)

        _tbl = postquery(_tbl, params)

        if not _tbl.empty:
            _tbl.insert(4, 'arw', _tbl.apply(nonvec_rw, axis=1))

    else:
        _tbl = None

    return _tbl

@timeit
def maps(mps, cmps, params):
    _tbl = prequery(mps, params)

    if not _tbl.empty:
        _tbl = gb.maps(_tbl, cmps)

        _tbl = postquery(_tbl, params, ['timeplayed'])

    return _tbl

@timeit
def games(tbl):
    params = {}
    return prequery(tbl, params)

@timeit
def mod_comp(tbl, params):
    tbl = prequery(tbl[tbl.comp == params['comp']], params, ['hero_filter'])

    if 'map' not in params or params['map'] != 'ALL':
        session['maps'] = tbl.map.unique().tolist()

    tbl = gb.comp(tbl)

    tbl = postquery(tbl, params, ['timeplayed'])

    return tbl, session['maps']

@timeit
def game(mps, _params):
    _mps = mps.iloc[np.where(np.logical_or(mps.id_teamenemy==_params['left_id'], mps.id_teamenemy==_params['right_id']))]

    _teaml = _mps.player_team.iloc[0]
    _teamr = _mps.enemy_team.iloc[0]

    _maps = gb.game(_mps, ['player_team', 'map'])
    _all = gb.game(_mps, ['player_team'])
    _all['map'] = 'ALL'


    _maps = (_all[_all.player_team == _teaml].append(_maps[_maps.player_team == _teaml], ignore_index=True),
             _all[_all.player_team == _teamr].append(_maps[_maps.player_team == _teamr], ignore_index=True))

    _teams = (_teaml, _teamr)

    return _maps, _teams

@timeit
def mod_game(cmps, prf, params):
    _comps = prequery(cmps, params, ['timeplayed', 'side'])
    _perf = prequery(prf, params, ['timeplayed', 'side'])

    if 'side' in params:
        _left = int(params['side'])
        _right = abs(int(params['side'])-1)

        _comps = _comps.iloc[np.where(np.logical_or(
            np.logical_and(_comps.id_teamenemy == params['left_id'], _comps.side == _left),
            np.logical_and(_comps.id_teamenemy == params['right_id'], _comps.side == _right))
        )]

        _perf = _perf.iloc[np.where(np.logical_or(
            np.logical_and(_perf.id_teamenemy == params['left_id'], _perf.side == _left),
            np.logical_and(_perf.id_teamenemy == params['right_id'], _perf.side == _right)
        ))]
    else:
        _comps = cmps.iloc[np.where(np.logical_or(cmps.id_teamenemy == params['left_id'], cmps.id_teamenemy == params['right_id']))]
        _perf = prf.iloc[np.where(np.logical_or(prf.id_teamenemy == params['left_id'], prf.id_teamenemy == params['right_id']))]

    _gamelog = gl.log(list(_comps.fight)) if 'map' in params else None

    _comps, _perf = gb.mod_game(_comps,_perf)

    _comps = _comps[_comps.t > 30]
    _perf = _perf[_perf.t > 30]

    _comps = (_comps[_comps.player_team == params['left_team']], _comps[_comps.player_team == params['right_team']])
    _perf = (_perf[_perf.player_team == params['left_team']], _perf[_perf.player_team == params['right_team']])

    return _comps, _perf, _gamelog

@timeit
def mod_map(tbl, params):
    params['timeplayed'] = 0
    return comps(tbl, params)

@timeit
def sub_hth(cmp, plyr, params):
    _comps = prequery(cmp, params, ['hero'])

    def agg_perf_hero(tbl):
        return gb.hth(tbl)

    header = cmp.iloc[np.where(np.logical_and(cmp.comp == params['left'], cmp.enemy_comp == params['right']))]

    left_tbl = plyr.iloc[np.where(plyr.id_teamfight.isin(header.id_teamfight.values))]
    left_perf = agg_perf_hero(left_tbl)

    right_tbl = plyr.iloc[np.where(np.logical_and(plyr.fight.isin(header.fight.values), plyr.id_teamfight.isin(header.id_teamfight.values) == False))]
    right_perf = agg_perf_hero(right_tbl)

    _combined = left_perf.append(right_perf)

    return _combined.reset_index()
