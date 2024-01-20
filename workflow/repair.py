import os
import shutil

import jsonpickle as jp
from cv.classes.game_events import *

def generate_repair_dicts():
    _files = get_saved_rounds()

    _vars = {}

    for file in _files:
        with open(file) as _file:
            _filename = os.path.splitext(os.path.basename(file))[0]
            _text = _file.read()
            _json = jp.decode(_text)

            _load = next(x for y, x in enumerate(_json) if type(x) == EventMapLoaded)
            _joins = [x for y, x in enumerate(_json) if type(x) == EventJoinedTeam]

            _vars[_filename] = {
                'load': _load,
                'joins': _joins
            }

    return _vars

def get_saved_rounds():
    #Get list of video directories with 'ready' file in them.
    _videos = [c.LAB_VIDEOS + x + '/json' for x in next(os.walk(c.LAB_VIDEOS))[1] if os.path.isfile('%s%s/ready' % (c.LAB_VIDEOS, x))]

    #Get files from all of them and put them into files list.
    _files = []
    for v in _videos:
        for js in os.listdir(v):
            _files.append(os.path.join(v, js))

    return _files

def repair_saved_round(params):
    #Build out path structure in stages so we can cleanup later..
    _dir = '%s%s/' % (c.LAB_VIDEOS, params['filename'].split('.')[0])
    _jsdir = '%sjson/' % _dir
    _filepath = '%s%s.txt' % (_jsdir, params['filename'])

    with open(_filepath) as _file:
        _text = _file.read()
        _json = jp.decode(_text)

        _load = next(x for y, x in enumerate(_json) if type(x) == EventMapLoaded)
        _joins = [x for y, x in enumerate(_json) if type(x) == EventJoinedTeam]

        _load.map = params['map'].upper()
        _load.left_team = params['team0'].upper()
        _load.right_team = params['team1'].upper()
        _load.patch = params['patch'].upper()
        _load.region = params['region'].upper()

        _text = jp.encode(_json)

    for i, j in enumerate(_joins):
        if j.source.name != params['player%i' % i].upper():
            _text = _text.replace("\"" + j.source.name, "\"" + params['player%i' % i].upper())

    os.makedirs(os.path.dirname(c.LAB_UPLOAD), exist_ok=True)
    with open('%s%s.txt' % (c.LAB_UPLOAD, params['filename']), "w+") as text_file:
        text_file.write(_text)

    os.remove(_filepath)

    _files = next(os.walk(_jsdir))[2]

    if len(_files) == 0:
        shutil.rmtree(_dir)
