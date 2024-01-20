from flask import Flask, render_template
from workflow import builder as b
from workflow import renderer as r
from settings.timeit import timeit
import numpy as np

np.seterr(all='ignore')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'who gives a shit'
app.config['ENV'] = 'DEBUG'

@timeit
def data(key): return app.safe[key].copy()

@timeit
def preload():
    app.safe = b.preload()

app.preload = preload
app.preload()

#Primary pages
@app.route('/perf', methods=["GET", "POST"])
def perf():
    return r.perf(data('perf'))

@app.route('/comps', methods=["GET", "POST"])
def comps():
    return r.comps(data('comps'))

@app.route('/games')
def games():
    return r.games(data('games'))

@app.route('/maps',  methods=["GET", "POST"])
def maps():
    return r.maps(data('maps'), data('comps'))

@app.route('/teams')
def teams():
    return render_template('teams.html')

@app.route('/players')
def players():
    return render_template('players.html')

@app.route("/game", methods=["GET"])
def game():
    return r.game(data('maps'))

@app.route('/')
def index():
    return render_template('index.html')

#Modals
@app.route("/modal/comp", methods=["GET"])
def mod_comp():
    return r.modal_comp(data('comps'))

@app.route("/modal/map", methods=["GET"])
def mod_map():
    return r.modal_map(data('comps'))

@app.route("/modal/game", methods=["GET"])
def mod_game():
    return r.mod_game(data('comps'), data('perf'))

#Submodals
@app.route("/modal/submodal/hth", methods=["GET", "POST"])
def sub_hth():
    return r.sub_hth(data('comps'), data('perf'))

#Dev Pages
@app.route('/linker', methods=["GET", "POST"])
def linker():
    return r.dev_linker()

@app.route('/repair', methods=["GET", "POST"])
def repair():
    return r.dev_repair()

@app.route('/upload', methods=["GET", "POST"])
def upload():
    return r.dev_upload(app)

@app.route("/modal/watcher", methods=["GET"])
def mod_watcher():
    return r.modal_watcher()

@app.route("/modal/repair", methods=["GET"])
def mod_repair():
    return r.modal_repair()

if __name__ == '__main__':
    app.run(threaded=True)

