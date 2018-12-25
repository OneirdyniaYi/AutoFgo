# coding: utf-8
# Author: Why
from pymouse import PyMouse
from Xlib import display, X
from PIL import Image

# Global Varables:
LOADING_WAIT_TIME = 5
START_MISSION_EXTRA_SLEEP = 2
ATK_SLEEP_TIME = 0.2
SKILL_SLEEP1 = 0.2
SKILL_SLEEP2 = 0.2
SKILL_SLEEP3 = 0.2
ULTIMATE_SLEEP = 0.3


def ScreenShot(x1, y1, x2, y2):
    dsp = display.Display()
    root = dsp.screen().root
    # Args: get_image(x, y, width, height)
    raw = root.get_image(x1, y1, x2-x1, y2-y1, X.ZPixmap, 0xffffffff)
    return Image.frombytes("RGB", (x2-x1, y2-y1), raw.data, "raw", "BGRX")


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


if __name__ == '__main__':
    pass
