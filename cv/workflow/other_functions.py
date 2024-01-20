import os
import cv2
import time
from math import floor
from settings import constants as c

def get_file_name(path):
    return os.path.splitext(os.path.basename(path))[0]

def cv_error(image, name):
    print(c.LAB_DEBUG + str(name) + ".jpg")
    cv2.imwrite(c.LAB_DEBUG + str(name) + ".jpg", image)
    return None

def cv_window(image, name=str(time.time())):
    winname = name
    cv2.namedWindow(winname)  # Create a named window
    cv2.moveWindow(winname, floor(1920/2), floor(1080/2))  # Move it to (40,30)
    cv2.imshow(winname, image)
    cv2.waitKey()
    cv2.destroyAllWindows()