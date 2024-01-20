import os
import _pickle
import cv2
from cv.workflow import image_functions as a
from cv.workflow import other_functions as o
from cv.classes.game_objects import *
import numpy as np

class Frame(object):
    def __init__(self, image):
        self.image = image
        _, self.width, self.height = self.image.shape[::-1]

class Ability(object):
    def __init__(self, path, parent):
        self.image = a.split_image(path, c.MOD_GRAY)

        self.image_small = a.split_image(
            cv2.resize(cv2.imread(path), (0,0), fx=0.6, fy=0.6, interpolation = cv2.INTER_CUBIC),
            c.MOD_GRAY)

        self.name = o.get_file_name(path)
        self.parent = parent

class Hero(object):
    def __init__(self, path):
        self.name = o.get_file_name(path)
        self.image = a.split_image(path, c.MOD_GRAY)

class Number(object):
    def __init__(self, path):
        self.name = o.get_file_name(path)
        self.image = a.split_image(path, c.MOD_GRAY)

class Kill(object):
    def __init__(self, path):
        self.name = o.get_file_name(path)
        self.image = a.split_image(path, (c.MOD_GRAY, c.MOD_BGR))
        #self.image = a.resize_models(self.image, 0, self.image[c.HEIGHT], 6, self.image[c.WIDTH] - 6)
        self.team = None

    def instance(self):
        return _pickle.loads(_pickle.dumps(self, -1))

class Assist(object):
    def __init__(self, path):
        self.image = a.split_image(path, c.MOD_GRAY)
        self.name = o.get_file_name(path)
        self.team = None

    def instance(self):
        return _pickle.loads(_pickle.dumps(self, -1))

class Unit(object):
    def __init__(self, path, parent):
        self.name = o.get_file_name(path)
        self.image = a.split_image(path, (c.MOD_GRAY, c.MOD_BGR))
        self.team = None
        self.parent = parent

    def instance(self):
        return _pickle.loads(_pickle.dumps(self, -1))

class Matrix(object):
    def __init__(self, path, parent):
        self.name = o.get_file_name(path)
        self.image = a.split_image(path, (c.MOD_GRAY, c.MOD_BGR))
        self.team = None
        self.parent = parent

    def instance(self):
        return _pickle.loads(_pickle.dumps(self, -1))

class Herobar(object):
    def __init__(self, image):

        self.image = a.split_image(image, c.MOD_GRAY)
        self.slot_size = self.image[c.WIDTH]/6

        self.slice_right = list()
        self.slice_left = list()
        self.slice_pct = list()

        for x in range (0, 6):
            self.slice_right.append(a.resize_models(self.image,
                                                    0,
                                                    self.image[c.HEIGHT],
                                                    int((x + c.F_HEROBAR_SLICE_RATIO) * self.slot_size),
                                                    int((x + 1) * self.slot_size)))

            self.slice_left.append(a.resize_models(self.image,
                                   0,
                                   self.image[c.HEIGHT],
                                   int(x * self.slot_size) + 5,
                                   int((x + c.F_HEROBAR_SLICE_RATIO) * self.slot_size)))

            pts1 = np.float32([[8, 7], [34, 7], [1, 34], [27, 34]])
            pts2 = np.float32([[0, 0], [self.slice_left[x][c.WIDTH], 0], [0, self.slice_left[x][c.HEIGHT]], [self.slice_left[x][c.WIDTH], self.slice_left[x][c.HEIGHT]]])
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            result = cv2.warpPerspective(self.slice_left[x][c.MOD_GRAY], matrix, (self.slice_left[x][c.WIDTH], self.slice_left[x][c.HEIGHT]))
            #_, result = cv2.threshold(result,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

            self.slice_pct.append(a.split_image(result, c.MOD_GRAY))

class Namebox(object):
    def __init__(self, image):
        self.image = a.split_image(image, c.MOD_GRAY)
        self.slot_size = self.image[c.WIDTH]/6

        self.namebox_slice = list()

        for x in range(0, 6):
            self.namebox_slice.append(self.image[c.MOD_GRAY][0:self.image[c.HEIGHT], int(x * self.slot_size) + 5:int((x + 1) * self.slot_size) - 7])

class Killfeed(object):
    def __init__(self, image):
        self.image = a.split_image(image, (c.MOD_GRAY, c.MOD_BGR))
        self.events = list()

class KillfeedEvent(object):
    def __init__(self, entity, player, type):
        self.entity = entity
        self.player = player
        self.type = type

class Match(object):
    def __init__(self, entity, min, pos):
        self.entity = entity
        self.min = min
        self.x = pos[0]
        self.y = pos[1]
        self.color = None

class Objective(object):
    def __init__(self, path):
        self.state = o.get_file_name(path)
        self.dir =  os.path.basename(os.path.dirname(path))
        self.image = a.split_image(path, (c.MOD_GRAY, c.MOD_BGR))

class Objectives(object):
    def __init__(self, path):
        self.image = a.split_image(path, (c.MOD_GRAY, c.MOD_BGR))

class Ultimate(object):
    def __init__(self, path):
        self.image = a.split_image(path, c.MOD_GRAY)

class Replay(object):
    def __init__(self, path):
        self.image = a.split_image(path, c.MOD_GRAY)






