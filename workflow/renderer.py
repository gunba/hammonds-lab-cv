import os
from flask import render_template, request
from workflow import aggregator as ag
from settings.timeit import timeit
from workflow import builder as b
from workflow import uploader as u
from workflow import repair as r
from workflow import watcher as w
from workflow import decorator as d
from settings import constants as c

_const = b.defaults()

def pandas_to_html(table, cls, idattr):
    return table \
        if table is None \
        else table.round(2).to_html(classes='%s' % cls,
                                     table_id=idattr,
                                     header=True,
                                     index=False,
                                     escape=False,
                                     formatters=d.applymap(list(table)))

@timeit
def perf(data, _table = None):
    _params = build_params()
    if request.method == "POST" and request.form['load'] == 'load':
        _table = ag.fights(data, _params)
        _table = pandas_to_html(_table, 'perf', 'main')
    return page('perf', _table, _params)

@timeit
def comps(tbl, _table = None):
    _params = build_params()
    if request.method == "POST" and request.form['load'] == 'load':
        _table = ag.comps(tbl, _params)
        _table = pandas_to_html(_table, 'comps', 'main')
    return page('comps', _table, _params)

@timeit
def maps(mps, cmps, _table = None):
    _params = build_params()
    if request.method == "POST" and request.form['load'] == 'load':
        _table = ag.maps(mps, cmps, _params)
        _table = _table.round(2)
        _table = d.applypandas(_table)
    return render_template('maps.html',
                           table=_table,
                           const=_const,
                           params=_params)

@timeit
def games(mps):
    _params = build_params()
    _table = ag.games(mps)
    _table = pandas_to_html(_table, 'games', 'main')
    return render_template('games.html',
                           table=_table,
                           const=_const,
                           params=_params)

@timeit
def page(html, table, params):
    return render_template('%s.html' % html,
                           table=table,
                           const=_const,
                           params=params)
@timeit
def modal_comp(tbl):
    _params = build_params()
    _table, _params['maps'] = ag.mod_comp(tbl, _params)
    _table = pandas_to_html(_table, 'comps', 'comp')

    return render_template('modal/comp.html',
                           table=_table,
                           params=_params,
                           heroify=d.multi_heroify(_params['comp'], 'modal-comp'))

@timeit
def modal_map(tbl):
    _params = build_params()
    _table = ag.mod_map(tbl, _params)
    _table = pandas_to_html(_table, 'maps', 'main')
    return render_template('modal/map.html',
                           table=_table,
                           params=_params)

@timeit
def game(mps):
    _params = build_params()
    _maps, _teams = ag.game(mps, _params)
    return render_template('game.html',
                           maps=[d.applypandas(_maps[0].round(2)), d.applypandas(_maps[1].round(2))],
                           teams=(_teams[0], _teams[1]),
                           params=_params)

def mod_game(cmps, prf):
    _params = build_params()
    _comps, _perf, _gamelog = ag.mod_game(cmps, prf, _params)
    return render_template('modal/game.html',
                           comps=(pandas_to_html(_comps[0], 'game comps compsl', 'scompl'), pandas_to_html(_comps[1], 'game comps compsr', 'scompr')),
                           perfs=(pandas_to_html(_perf[0], 'game perf perfl', 'sperfl'), pandas_to_html(_perf[1], 'game perf perfr', 'sperfr')),
                           gamelog=_gamelog,
                           params=_params)

@timeit
def sub_hth(cmp, prf):
    params = build_params()

    _table = ag.sub_hth(cmp, prf, params)
    _table = pandas_to_html(_table, 'hth', 'hth')

    return render_template('modal/submodal/hth.html',
                           table=_table,
                           params=params)

def build_params():
    _params = {}

    _defaults = {
         'timeplayed': 1000,
         'mindate': _const['mindate'],
         'maxdate': _const['maxdate']
     }

    #Merge form (ui) and request (?=x)
    _combined = {**request.form, **request.args}

    #Add them all to params if not ''
    for key, value in _combined.items():
        if value and value != "''":
            _params[key] = value

    #Fill in missing with defaults
    for key, value in _defaults.items():
        if key not in _params:
            _params[key] = value

    print(_params)

    return _params

#Dev renders below (i.e. doesn't matter)
@timeit
def dev_linker():
    _params = build_params()
    if request.method == "POST" and request.form['load'] == 'load':
        _info = w.get_video_metadata(_params)
        return render_template('dev/watcher.html',
                               info=_info,
                               ui=[x[0] for x in _const['selects'] if x[1] == 'UI'])
    else:
        return render_template('dev/linker.html')

@timeit
def dev_repair():
    _params = build_params()
    _repairs = r.generate_repair_dicts()
    return render_template('dev/repair.html',
                           repairs=_repairs,
                           maps=sorted([x[0] for x in  _const['selects'] if x[1] in ('ESCORT', 'HYBRID', 'ASSAULT', 'CONTROL')]),
                           patches=[x[0] for x in _const['selects'] if x[1] == 'PATCH'],
                           regions=[x[0] for x in _const['selects'] if x[1] == 'REGION'])

def dev_upload(app):
    if request.method == "POST" and request.form['load'] == 'load':
        u.upload_stored_json(app)
        return render_template('index.html')
    else:
        return render_template('dev/upload.html',
                               json = len(os.listdir(c.LAB_UPLOAD)))

@timeit
def modal_watcher():
    _params = build_params()
    w.run_video_thread(_params)
    return 'foo' #Need a string return min.

@timeit
def modal_repair():
    _params = build_params()
    r.repair_saved_round(_params)
    return 'foo'