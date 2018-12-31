# coding: utf-8
# Author: Why
from pymouse import PyMouse
from PIL import Image
import numpy as np
import logging
from pykeyboard import PyKeyboardEvent
import time

# Global Varables:
ROOT = '/run/media/why/OS/WHY/Why酱の工具箱/fgo/'
ATK_SLEEP_TIME = 0.15
ULTIMATE_SLEEP = 0.2
SKILL_SLEEP1 = 0.15
SKILL_SLEEP2 = 0.2
SKILL_SLEEP3 = 0.3
CLICK_BAR_SLEEP = 0.2
EXTRA_SLEEP_UNIT = 0.05      # defalut 0.1
# LOADING_WAIT_TIME = 5       # time sleep before loading.
# WAIT_LOADING_SLEEP = 1      # sanp between loadings

# LOG:
# - pyscreenshot: too slow
# - pyautogui: Good. A little slow.

# NOT STABLE: have strange black block
# - Xlib and Xorg: sometimes get strange screenshot (WTF is it?!)
# - GTK3: can't install.
# - autopy: fastest, but need I/O (Althpugh the fastest), return `autopy.bitmap` can't use `!=` to compare.

# not stable but quick, used during battle.


def ScreenShot(x1, y1, x2, y2, to_PIL=False, fname=None):
    import autopy
    # print(x1, y1, x2, y2, 'size:', x2-x1, y2-y1)
    im = autopy.bitmap.capture_screen(((x1, y1), (x2-x1, y2-y1)))
    if fname:
        im.save(ROOT + 'data/{}.png'.format(fname))
    if to_PIL:
        # return PIL_img, bitmap_img
        im.save(ROOT + 'data/tmp.png')
        return Image.open(ROOT + 'data/tmp.png').convert('RGB'), im
    else:
        return im


# def ScreenShot(x1, y1, x2, y2):
#     from Xlib import display, X
#     dsp = display.Display()
#     root = dsp.screen().root
#     # Args: get_image(x, y, width, height)
#     raw = root.get_image(x1, y1, x2-x1, y2-y1, X.ZPixmap, 0xffffffff)
#     return Image.frombytes("RGB", (x2-x1, y2-y1), raw.data, "raw", "BGRX")


# # C_version:
# import os
# import ctypes
# LibName = 'prtscn.so'
# AbsLibPath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + LibName
# grab = ctypes.CDLL(AbsLibPath)
# def ScreenShot(x1, y1, x2, y2):
#     w, h = x2-x1, y2-y1
#     size = w * h
#     objlength = size * 3
#     grab.getScreen.argtypes = []
#     result = (ctypes.c_ubyte*objlength)()

#     grab.getScreen(x1, y1, w, h, result)
#     return Image.frombuffer('RGB', (w, h), result, 'raw', 'RGB', 0, 1)


# def ScreenShot(x1, y1, x2, y2):
#     import pyscreenshot as ImageGrab
#     return ImageGrab.grab(bbox=(x1, y1, x2, y2))

# stable, used out of battle.


# def grab_acc(x1, y1, x2, y2):
#     import pyautogui
#     # button7location = pyautogui.locateOnScreen('./debug/ori.png')
#     return pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))


class SpecialFormatter(logging.Formatter):
    base = '\033[0;{}m>> {}-%(asctime)s - %(message)s\033[0m'
    FORMATS = {logging.DEBUG: base.format(35, 'D'),
               logging.ERROR: base.format(31, 'E'),
               logging.INFO: base.format(32, 'I'),
               logging.WARN: base.format(33, 'W')}

    def format(self, record):
        datefmt = '%H:%M:%S'
        tmp_fmter = logging.Formatter(self.FORMATS.get(
            record.levelno), datefmt=datefmt)
        return tmp_fmter.format(record)


def get_log():
    # date_fmt = '%m-%d %H:%M:%S'
    file_fmt = '> %(asctime)s:%(levelname)s - %(message)s'
    file_date_fmt = '%H:%M'
    logging.basicConfig(level=logging.INFO, format=file_fmt,
                        datefmt=file_date_fmt, filename=ROOT + 'data/fgo.LOG', filemode='w')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # if DEBUG:
    #     console.setLevel(logging.DEBUG)
    console.setFormatter(SpecialFormatter())
    logging.getLogger().addHandler(console)


class Cursor(object):
    def __init__(self, init_pos):
        # init_pos： type:tuple, set `False` to skip initing position.
        self.c = PyMouse()
        if init_pos != False and len(init_pos) == 2:
            self.move_to(init_pos)

    def move_to(self, pos):
        self.c.move(pos[0], pos[1])

    def get_pos(self):
        return self.c.position()

    def click(self, pos):
        self.c.click(pos[0], pos[1], 1)

    def get_screen_wh(self):
        return self.c.screen_size()


class KeyEventListener(PyKeyboardEvent):
    def tap(self, keycode, character, press):
        '''
        Args:
        ------
        keycode: Number ID for input key.
        character: character of the input key.
        press: BOOL, True for press, False for release
        '''
        print('keycode:', keycode, 'character:', character, 'press:', press)
        if character in ('P'):
            self.stop()


# def get_wallpaper_RGB():
#     pic = ScreenShot(0, 0, 10, 10)
#     print(np.array(pic, dtype=np.uint8).mean(axis=(0, 1)))


if __name__ == '__main__':
    # get_wallpaper_RGB()
    pass
