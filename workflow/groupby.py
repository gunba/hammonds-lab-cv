import pandas as pd
from settings.timeit import timeit

pd.set_option('precision', 5)

_applies = {
    #PERF/GLOBAL
    'perf': {
        't': lambda x: x.tp.sum(),
        'fw': lambda x: x.result.sum() / x.result.count(),
        'fwv': lambda x: (x.result.sum() / x.result.count()).var(),
        'i': lambda x: x.i.sum() / x.pf.sum(),
        'i50': lambda x: (x.iw.sum() / x.pfxr.sum() + x.il.sum() / x.pfnxr.sum()) / 2,
        'i50v': lambda x: ((x.iw.sum() / x.pfxr.sum() + x.il.sum() / x.pfnxr.sum()) / 2).var(),
        'ue': lambda x: x.ue.sum() / x.pf.sum(),
        'u50': lambda x: (x.uew.sum() / x.pfxr.sum() + x.uel.sum() / x.pfnxr.sum()) / 2,
        'u50v': lambda x: ((x.uew.sum() / x.pfxr.sum() + x.uel.sum() / x.pfnxr.sum()) / 2).var(),
        'kpa': lambda x: (x.kills.sum() + x.assists.sum()) / x.teamkills.sum(),
        'kdr': lambda x: (x.kills.sum() + (x.assists.sum()*0.15)) / x.deaths.sum(),
        'kpf': lambda x: x.kills.sum() / x.pf.sum(),
        'dpf': lambda x: x.deaths.sum() / x.pf.sum(),
        'apf': lambda x:  x.assists.sum() / x.pf.sum(),
        'aspf': lambda x: x.assisted.sum() / x.pf.sum(),
        'upf': lambda x: x.ults.sum() / x.pf.sum(),
        'fk%': lambda x: x.fk.sum() / x.teamfk.sum(),
        'fd%': lambda x: x.fd.sum() / x.teamfd.sum(),
        'fa%': lambda x:  x.fa.sum() / x.teamfa.sum(),
        'ugt': lambda x: x.ultgain.mean(),
        'uht': lambda x: x.ultheld.mean(),
        'uut': lambda x:  x.ultuse.mean(),
        'fkw': lambda x: (x.rafk > 0).sum() / x.fkbool.sum(),
        'fdw': lambda x: (x.rafd > 0).sum() / x.fdbool.sum(),
        'faw': lambda x: (x.rafa > 0).sum() / x.fabool.sum(),
        'mpf': lambda x: x.matrixes.sum() / x.pf.sum(),
        'mat':lambda x: x.matrixed.sum() / x.ults.sum(),
        'um': lambda x: x.umar.sum() / x.umbool.sum(),
        'ufw': lambda x: x.usar.sum() / x.ubool.sum(),
        'upd': lambda x:  x.ultdiff.mean(),
        'uud': lambda x:  x.usediff.mean(),
        'upa': lambda x:  x.prev_ult_used.sum() / x.ults.sum(),
        'upt': lambda x: x.prev_team_ult_used.sum() / x.ults.sum(),
        'kp': lambda x: x.kpos.sum() / x.kills.sum(),
        'dp': lambda x: x.dpos.sum() / x.deaths.sum(),
        'ap': lambda x: x.apos.sum() / x.assists.sum(),
        'kt': lambda x: x.ktime.sum() / x.kills.sum(),
        'dt': lambda x: x.dtime.sum() / x.deaths.sum(),
        'at': lambda x: x.atime.sum() / x.assists.sum(),
        'ku': lambda x: x.kult.sum() / x.kills.sum(),
        'du': lambda x: x.dult.sum() / x.deaths.sum(),
        'au': lambda x: x.ault.sum() / x.assists.sum(),
    },

    #COMP
    'comp': {
        't': lambda x: x.tp.sum(),
        'kcr': lambda x: x.kpadk.corr(x.result),
        'ucr': lambda x: x.ults.corr(x.result),
        'kdr': lambda x: (x.kills.sum() + x.assists.sum()) / x.deaths.sum(),
        'fk%': lambda x: x.fkgtfd.sum() / x.tp.count(),
        'fd%': lambda x: x.fkltfd.sum() / x.tp.count(),
        'fkw': lambda x: x.rafkgtfd.sum() / x.fkgtfd.sum(),
        'fdw': lambda x: x.rafkltfd.sum() / x.fkltfd.sum(),
        'kpa': lambda x: (x.kills.sum() + x.assists.sum()) / x.kills.sum() / 6,
        'upw': lambda x: x.usar.sum() / x.ubool.sum(),
        'spf': lambda x: x.swaps.sum() / x.pf.sum(),
        'modal_comp': lambda x: x.comp.iloc[0],
        'modal_enemy': lambda x: x.enemy_comp.iloc[0],
        'fw': lambda x: x.result.sum() / x.result.count(),
        'f': lambda x: x.result.count(),
        'created': lambda x: x.created.iloc[0],

        #PERF IMPORTS
        'kpf': lambda x: x.kills.sum() / x.pf.sum(),
        'dpf': lambda x: x.deaths.sum() / x.pf.sum(),
        'apf': lambda x: x.assists.sum() / x.pf.sum(),
        'ugt': lambda x: x.ultgain.mean(),
        'uht': lambda x: x.ultheld.mean(),
        'uut': lambda x: x.ultuse.mean(),
        'kt': lambda x: x.ktime.sum() / x.kills.sum(),
        'dt': lambda x: x.dtime.sum() / x.deaths.sum(),
        'upf': lambda x: x.ults.sum() / x.pf.sum(),
        'upa': lambda x: x.prev_ult_used.sum() / x.ults.sum(),
    },

    #MAP
   'map': {
        't': lambda x: x.tp.sum(),
        'fwm': lambda x: x.fw.sum() / x.f.sum(),
        'saw': lambda x: (x.fw * (x.start == 1)).sum() / (x.f * (x.start == 1)).sum(),
        'sdw': lambda x: (x.fw * (x.start == 0)).sum() / (x.f * (x.start == 0)).sum(),
        'aw': lambda x: x.fwxsi0.sum() / x.fxsi0.sum(),
        'aw1': lambda x: x.fwxob1si0.sum() / x.fxob1si0.sum(),
        'aw2': lambda x: x.fwxob2si0.sum() / x.fxob2si0.sum(),
        'aw3': lambda x: x.fwxob3si0.sum() / x.fxob3si0.sum(),
        'dw': lambda x: x.fwxsi1.sum() / x.fxsi1.sum(),
        'dw1': lambda x: x.fwxob1si1.sum() / x.fxob1si1.sum(),
        'dw2': lambda x: x.fwxob2si1.sum() / x.fxob2si1.sum(),
        'dw3': lambda x: x.fwxob3si1.sum() / x.fxob3si1.sum(),
        'f': lambda x: x.f.sum(),
        'f1': lambda x: x.fxob1.sum(),
        'f2': lambda x: x.fxob2.sum(),
        'f3': lambda x: x.fxob3.sum(),
        'fw1': lambda x: x.fwxob1.sum() / x.fxob1.sum(),
        'fw2': lambda x: x.fwxob2.sum() / x.fxob2.sum(),
        'fw3': lambda x: x.fwxob3.sum() / x.fxob3.sum(),
        'flen': lambda x: x.tp.sum() / x.f.sum(),
        'aprog': lambda x: (x.prog * (x.side==0)).mean(),
        'dprog': lambda x: (x.prog * (x.side==1)).mean(),
        'rlw': lambda x: x.fwxsi2.sum() / x.fxsi2.sum(),
        'mode': lambda x: x['mode'].iloc[0],
    }
}

@timeit
def applymap(cols, row, name):
    _lamb = {}

    for x in cols:
        if x not in _applies[name]:
            print('WARNING: %s not in applymap.' % x)
        else:
            _lamb[x] = _applies[name][x](row)

    return _lamb

@timeit
def fights(tbl, groupby):
    tbl = tbl.groupby(groupby).apply(lambda x: pd.Series(
        applymap(
            ['t', 'fw', 'i50', 'u50', 'kpa', 'kdr', 'kpf', 'dpf', 'apf', 'upf', 'fk%', 'fd%',
             'fa%', 'ugt', 'uht', 'fkw', 'fdw', 'mat', 'upt'], x, 'perf')
    )).reset_index()

    tbl = tbl.rename(index=str, columns={"player_team": "team"})
    return tbl

@timeit
def comps(tbl):
    tbl = tbl.groupby(['comp']) \
        .apply(lambda x: pd.Series(
        applymap(['t', 'f', 'fw', 'kcr', 'ucr', 'kpa', 'kdr', 'kpf', 'dpf', 'apf', 'fk%', 'fd%', 'upw', 'upf',
                  'ugt', 'uht', 'fkw', 'fdw', 'upa', 'kt', 'dt', 'modal_comp'], x, 'comp')

    )).reset_index()
    return tbl

@timeit
def maps(_tbl, cmps):
    _tbl = _tbl.groupby(['map']). \
        apply(lambda x: pd.Series(
        applymap(['t', 'saw', 'sdw', 'aw', 'aw1', 'aw2', 'aw3', 'dw', 'dw1', 'dw2', 'dw3',
                  'f', 'f1', 'f2', 'f3', 'fwm', 'fw1', 'fw2', 'fw3', 'flen', 'aprog', 'dprog', 'rlw', 'mode'], x, 'map')
    )).reset_index()

    return _tbl

@timeit
def comp(tbl):
    tbl = tbl.groupby(['enemy_comp']) \
        .apply(lambda x: pd.Series(
        applymap(['t', 'f', 'fw', 'kcr', 'ucr', 'kpa', 'kdr',
                  'kpf', 'dpf', 'apf', 'fk%', 'fd%', 'upw', 'upf', 'ugt', 'uht', 'fkw', 'fdw', 'upa', 'kt',
                  'dt', 'modal_enemy'], x, 'comp')

    )).reset_index()
    tbl = tbl.rename(index=str, columns={"enemy_comp": "comp"})
    return tbl

@timeit
def hth(tbl):
    return tbl.groupby(['hero']) \
        .apply(lambda x: pd.Series(applymap(
        ['i', 'ue', 'kpa', 'kdr', 'kpf', 'dpf', 'apf', 'aspf', 'upf', 'fk%', 'fd%', 'ugt', 'uht', 'fkw',
         'fdw', 'mtp', 'mat', 'um', 'ufw', 'upa', 'kp', 'dp', 'ap', 'kt', 'dt'], x, 'perf')))

@timeit
def game(_maps, groupby):
    _maps = _maps.groupby(groupby). \
        apply(lambda x: pd.Series(
        applymap(['t', 'f', 'fwm', 'fw1', 'fw2', 'fw3', 'aw', 'aw1', 'aw2', 'aw3', 'dw', 'dw1', 'dw2', 'dw3', 'flen',
                  'aprog', 'dprog', 'mode', 'rlw'], x, 'map'))).reset_index()
    return _maps

@timeit
def mod_game(_comps, _perf):
    _comps = _comps.groupby(['player_team', 'comp']). \
        apply(lambda x: pd.Series(
        applymap(['t', 'f', 'fw', 'kdr', 'fk%', 'fd%', 'upw', 'fkw', 'fdw'], x, 'comp'))).reset_index()

    _perf = _perf.groupby(['player_team', 'hero', 'name']). \
        apply(lambda x: pd.Series(
        applymap(['t', 'i50', 'u50', 'kpa', 'kdr', 'fk%', 'fd%', 'ugt'], x, 'perf'))).reset_index()

    return _comps, _perf


