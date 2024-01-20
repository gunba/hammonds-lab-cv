import io
from base64 import b64encode
import matplotlib.pyplot as plt

plt.style.use('dark_background')

def buffer(ax):
    formatter(ax)
    img = io.BytesIO()
    fig = ax.get_figure()
    fig.savefig(img, format='png', bbox_inches='tight', facecolor=(0.114, 0.114, 0.114))
    img.seek(0)
    return b64encode(img.read()).decode("utf-8")


def formatter(ax):
    plt.setp(ax.get_xticklabels(), rotation=45, fontsize=8)
    ax.xaxis.set_label_text("")
    ax.yaxis.set_label_text("")
    ax.get_legend().set_title(None)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_facecolor((0.114, 0.114, 0.114))
    _leg = ax.legend().get_frame()
    _leg.set_linewidth(0.0)
    _leg.set_fill(False)


def plot_ad(t):
    t["map"] = t["map"].str.replace(' ', '\n')
    ax = t.pivot("map", "side", "mfw").plot(kind='bar', figsize=(6.7, 4), sort_columns=True, colormap=plt.cm.get_cmap('tab20c'))
    ax.title.set_text('Fight winrate vs. side/map')
    return buffer(ax)

def plot_t(t):
    t["map"] = t["map"].str.replace(' ', '\n')
    t["f*fln"] = t['f#'] * 33
    ax = t.plot(x='map', y=['t', 'f*fln'], kind='bar', figsize=(6.7, 4), sort_columns=True, colormap=plt.cm.get_cmap('tab20c'))
    ax.title.set_text('Fightlen: actual vs expected')
    return buffer(ax)

_lamb = {
    'ad': lambda x: plot_ad(x),
    't': lambda x: plot_t(x)
}

def maps(plots, _plots = None):

    if plots:
        _plots = {}

        for key, value in plots.items():
            if key in _lamb:
                _plots[key] = _lamb[key](value)

    return _plots

