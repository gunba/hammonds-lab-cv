import base64
import math
import time

import cv2
import numpy as np
import PIL.Image
from scipy.interpolate import UnivariateSpline
from settings import constants as c
from io import BytesIO
import cv.workflow.other_functions as o

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

def split_image(image, model_list):
    if type(image) == str:
        image = cv2.imread(image)

    model_dict = dict()
    model_dict[c.MOD_GRAY] = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim > 2 else image

    if c.MOD_BGR in model_list:
        model_dict[c.MOD_BGR] = image
        model_dict[c.MOD_QUAD] = quad(image)

    model_dict[c.WIDTH], model_dict[c.HEIGHT] = get_size(model_dict[c.MOD_GRAY])

    return model_dict

def get_size(image):
    shape = image.shape
    return shape[1], shape[0]

def resize_models(model_dict, y1, y2, x1, x2):
    t_dict = model_dict.copy()
    for key in model_dict:
        if key not in c.T_NON_IMAGE:
            t_dict[key] = model_dict[key][y1:y2, x1:x2]

    t_dict[c.WIDTH] = int(x2-x1)
    t_dict[c.HEIGHT] = int(y2-y1)
    return t_dict

def increase_brightness(image):
    brightness = 50
    contrast = 100
    image = np.int16(image)
    image = image * (contrast / 127 + 1) - contrast + brightness
    image = np.clip(image, 0, 255)
    image = np.uint8(image)
    return image

def blackout_models(model_dict, y1, y2, x1, x2):
    for key in model_dict:
        if key not in c.T_NON_IMAGE:
            model_dict[key] =   blackout_image(model_dict[key], y1, y2, x1, x2)
    return model_dict

def blackout_image(image, y1, y2, x1, x2):
    t_image = np.ascontiguousarray(image, dtype=np.uint8)
    t_image = cv2.rectangle(t_image, (x1, y1), (x2, y2), (0, 0, 0), thickness=cv2.FILLED)
    return t_image

def otsu_image(image):
    _, otsu = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return otsu

def ocr_image(img, font):
    img = cv2.resize(img, None, fx=7, fy=7, interpolation=cv2.INTER_LANCZOS4)
    img = cv2.fastNlMeansDenoising(img, 40, 40, 7, 21)
    _, img = cv2.threshold(img, 195, 255, cv2.THRESH_BINARY)

    #_, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    result_data = pytesseract.image_to_data(img, lang=font, config='--psm 7', output_type=pytesseract.Output.DICT)

    character_len = len(result_data['level'])
    name_builder = ""
    for x in range(0, character_len):
        name_builder += result_data['text'][x]

    o.cv_error(img, name_builder + "." + str(time.time()))

    return name_builder

def increase_red(img):
    def create_lut(x, y):
        spl = UnivariateSpline(x, y)
        return spl(range(256))

    inc_lut = create_lut([0, 50, 100, 192, 256],
                          [0, 50, 120, 215, 256])

    b, g, r = cv2.split(img)
    r = cv2.LUT(r, inc_lut).astype(np.uint8)

    return r

def canny_image(image):
    return cv2.Canny(image, 100, 200)

def avg_color(image, bm):
    if bm == c.B_WG:
        return image[image != 0].mean()
    else:
        b = image[:, :, 0]
        g = image[:, :, 1]
        r = image[:, :, 2]
        return b[b != 0].mean(), g[g != 0].mean(), r[r != 0].mean()

def compare_color(_one, _two):
    return sum([abs(_one[:, :, x].mean() - _two[:, :, x].mean())/3 for x in range(0, 3)])

def quad(_array):
    _aw, _ah = get_size(_array)

    _roi = _array[0:_ah, math.floor(0.25*_aw):math.floor(0.75*_aw)]
    _rw, _rh = get_size(_roi)

    _quads = list()
    _quads.append(_roi[0:math.floor(_rh / 3), 0:_rw])
    _quads.append(_roi[math.floor(_rh / 3):math.floor((_rh / 3)*2), 0:_rw])
    _quads.append(_roi[math.floor((_rh / 3)*2):math.floor((_rh / 3)*3), 0:_rw])
    return _quads

def get_edge_color(target, y1, y2, x1, x2, bm):
    t_target = blackout_image(target, y1, y2, x1, x2)
    return avg_color(t_target, bm)

def numpy_to_jpg(frame):
    frame_image = PIL.Image.fromarray(frame)
    out = BytesIO()
    frame_image.save(out, 'jpeg', quality=90, optimize=True)
    out.seek(0)
    return base64.b64encode(out.getvalue()).decode()