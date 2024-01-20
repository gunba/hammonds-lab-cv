import re
import youtube_dl
from multiprocessing.dummy import Pool as ThreadPool
from cv.classes.generator import Generator
from settings import constants as c

pool = ThreadPool(16)

_ytformat = {'format': '137',
             'outtmpl': c.LAB_VIDEOS + '%(id)s/%(id)s.%(ext)s'}

_ttvformat = {'format_id': '1080p60',
              'outtmpl': c.LAB_VIDEOS + '%(id)s/%(id)s.%(ext)s',
              'twitch-token': 'uk6f11510em0brw62hhhvyof2yrf4j',
              'ext': 'mp4',
              'postprocessors': [{
                  'key': 'FFmpegFixupM3u8'
              }]}

_reg = "/https?:\/\/(?:[0-9A-Z-]+\.)?(?:youtu\.be\/|youtube\.com(?:\/embed\/|\/v\/|\/watch\?v=|\/ytscreeningroom\?v=|\/feeds\/api\/videos\/|\/user\S*[^\w\-\s]|\S*[^\w\-\s]))([\w\-]{11})[?=&+%\w-]*/ig"
_genericyt = "https://youtu.be/%s"
_genericttv = "https://www.twitch.tv/videos/%s"

def get_video_metadata(params):
    urls = params['urls'].split('\r\n')
    _data = {}
    for url in urls:
        _url, _format = sanitize_url_and_format(url)
        with youtube_dl.YoutubeDL(_format) as ydl:
            _info = ydl.extract_info(_url, download=False)
            _data[_url] = _info
    return _data

def download_video(url):
    _url, _format = sanitize_url_and_format(url)
    with youtube_dl.YoutubeDL(_format) as ydl:
        print(_format)
        print(url)
        ydl.download([_url])

def process_video(url, params):
    _path = '%s%s/' % (c.LAB_VIDEOS, params['url'])

    download_video(url)

    run_steve(params, _path, url)

    open(_path + "ready", 'w').close()


def run_steve(params, path, url):
    Generator(params, path, url)

def sanitize_url_and_format(url):
    _url = match_youtube_string(url)
    _format = _ytformat if 'youtu.be' in url else _ttvformat
    return _url, _format

def match_youtube_string(url):
    result = re.search(_reg, url)
    return url if not result else _genericyt % result.match(0)

def run_video_thread(params):
    _url = _genericyt % params['url'] if params['url'][0] != 'v' else _genericttv % params['url'][1:]

    print(_url)

    process_video(_url, params)


