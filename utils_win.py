# coding: utf-8
# Author: Why
import win32api
import win32con
from PIL import ImageGrab
import logging

# Global Varables:
ROOT = '/run/media/why/OS/WHY/Why酱の工具箱/fgo/'
ATK_SLEEP_TIME = 0.1
ULTIMATE_SLEEP = 0.2
SKILL_SLEEP1 = 0.1
SKILL_SLEEP2 = 0.1
SKILL_SLEEP3 = 0.2
CLICK_BAR_SLEEP = 0.1
EXTRA_SLEEP_UNIT = 0


def ScreenShot(x1, y1, x2, y2, to_PIL=False, fname=None):
    im = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    if fname:
        im.save(ROOT + 'data/{}.png'.format(fname))
    return (im, im) if to_PIL else im


class SpecialFormatter(logging.Formatter):
    base = '>> {}-%(asctime)s - %(message)s'
    FORMATS = {logging.DEBUG: base.format('D'),
               logging.ERROR: base.format('E'),
               logging.INFO: base.format('I'),
               logging.WARN: base.format('W')}

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
        if init_pos != False and len(init_pos) == 2:
            self.move_to(init_pos)

    def move_to(self, pos):
        win32api.SetCursorPos(pos)

    def get_pos(self):
        return win32api.GetCursorPos()

    def click(self, pos):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def right_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def get_screen_wh(self):
        return win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(win32con.SM_CYSCREEN)


def test():
    img = ImageGrab.grab()
    img.save('FullScreenGrab.jpg')


if __name__ == '__main__':
    test()
