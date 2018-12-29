# coding: utf-8
# Author: Why
import win32api
import win32con
from PIL import ImageGrab
import logging

# Global Varables:
ROOT = '/run/media/why/OS/WHY/Why酱の工具箱/fgo/'
LOADING_WAIT_TIME = 3
ATK_SLEEP_TIME = 0.1
SKILL_SLEEP1 = 0.1
SKILL_SLEEP2 = 0.1
SKILL_SLEEP3 = 0.2
ULTIMATE_SLEEP = 0.2
CLICK_BAR_SLEEP = 0.1
EXTRA_SLEEP_UNIT = 0
WAIT_LOADING_SLEEP = 1      # sanp between loadings


# in Windows, 2 kinds of grab method is the same.
# THese strange settings is for match linux API.
def ScreenShot(x1, y1, x2, y2, to_PIL=False, fname=None):
    im = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    if fname:
        im.save(ROOT + 'data/{}.png'.format(fname))
    return (im, im) if to_PIL else im


def get_log():
    fmt = '%(asctime)s:%(levelname)s - %(message)s'
    # date_fmt_echo = '%m-%d %H:%M:%S'
    date_fmt_file = '%H:%M'
    logging.basicConfig(level=logging.DEBUG, format=fmt,
                        datefmt=date_fmt_file, filename=ROOT + 'data/fgo.LOG', filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # if DEBUG:
    #     console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(fmt, datefmt=date_fmt_file))
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
