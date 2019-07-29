# coding: utf-8
# author: Why
# version: 5.0
import argparse
import os
import sys
import time

import numpy as np
from PIL import Image

SYSTEM = sys.platform

if SYSTEM == 'linux':
    print('------------')
    print('>>> Current system: Linux')
    from utils_linux import *
else:
    from utils_win import *

# ===== Config: =====
CURRENT_EPOCH = 0
PRE_BREAK_TIME = CLICK_BREAK_TIME
Args = argparse.ArgumentParser()
Args.add_argument('--epoch', '-e', type=int, help='Num of running battles.')
Args.add_argument('--keep', '-k', type=int,
                  help='if 0: keep the window-position same as the last time; if n: load from file n')
Args.add_argument('--CheckPos', '-p', action='store_true',
                  help='To see the window-position, shoud be used with `--keep`.')
Args.add_argument('--debug', '-d', action='store_true',
                  help='Enter DEBUG mode.')
Args.add_argument('--shutdown', '-sd', action='store_true',
                  help='close the simulator after running.')
Args.add_argument('--locate', '-l', action='store_true',
                  help='Monitor cursor\'s  position.')
OPT = Args.parse_args()
# ===== Main Code: =====


# ===== update Global varibles: =====
KEEP_POSITION = False
DEBUG = False
EPOCH = 1
ONE_BATTLE_TIMEOUT = 600

KEEP_POSITION = OPT.keep if OPT.keep != None else KEEP_POSITION
DEBUG = OPT.debug if OPT.debug else DEBUG
EPOCH = OPT.epoch if OPT.epoch else EPOCH
if OPT.shutdown and SYSTEM == 'linux':
    input(
        '\033[1;31m>>> 警告：罗德岛主机将于行动结束后关闭，是否继续?\033[0m')
print('>>> 注意: 你正处于调试模式!' if DEBUG else '')


def info(str):
    logging.info('<E{}/{}> - {}'.format(CURRENT_EPOCH, EPOCH, str))


class Arknights(object):
    __slots__ = ('c', 'width', 'height', 'scr_pos1',
                 'scr_pos2', 'area', 'img', 'LoadImg')

    def __init__(self, full_screen=False, sleep=False):
        # [init by yourself] put cursor at the down-right position of the game window.
        self.c = Cursor(init_pos=False)
        if full_screen:
            self.width, self.height = self.c.get_screen_wh()
            self.scr_pos1 = (0, 0)
            self.scr_pos2 = (self.width, self.height)
            for x in range(5):
                logging.info(
                    'Start in %d s, Please enter FULL SCREEN.' % (5-x))
                time.sleep(1)
        else:
            if type(KEEP_POSITION) == int or OPT.CheckPos:
                with open(ROOT + 'data/INIT_POS.{}'.format(KEEP_POSITION), 'r') as f:
                    res = f.readlines()
                res = tuple([int(x) for x in res[0].split(' ')])
                self.scr_pos1 = res[:2]
                self.scr_pos2 = res[2:]
                if OPT.CheckPos:
                    self.c.move_to(self.scr_pos1)
                    time.sleep(0.5)
                    self.c.move_to(self.scr_pos2)
                    os._exit(0)
                if KEEP_POSITION == 0:
                    print('>>> 使用已保存的屏幕显示配置接入罗德岛.')
                elif KEEP_POSITION:
                    print('>>> Load init_pos from file', KEEP_POSITION)
            else:
                while 1:
                    print('>>> 正在配置屏幕显示设置 以接入罗德岛.')
                    if input('>>> Move cursor to <top-left>, then press ENTER (q to exit): ') == 'q':
                        print('>>> Running stop')
                        os._exit(0)
                    self.scr_pos1 = self.c.get_pos()
                    print('>>> Get cursor at {}'.format(self.scr_pos1))

                    if input('>>> Move cursor to <down-right>, then press ENTER (q to exit): ') == 'q':
                        print('>>> Running stop')
                        os._exit(0)
                    self.scr_pos2 = self.c.get_pos()
                    print('>>> Get cursor at {}'.format(self.scr_pos2))

                    res = input('是否继续? [y(continue) /n(reset) /q(quit)]:')
                    if res == 'n':
                        continue
                    elif res == 'q':
                        os._exit(0)
                    else:
                        break
                if sleep:
                    for x in range(3):
                        logging.info(
                            'Start in %d s, make sure the window not covered.' % (3-x))
                        time.sleep(1)
                with open(ROOT + 'data/INIT_POS.0', 'w') as f:
                    pos = str(self.scr_pos1[0]) + ' ' + str(self.scr_pos1[1]) + \
                        ' ' + str(self.scr_pos2[0]) + \
                        ' ' + str(self.scr_pos2[1])
                    f.write(pos)
                    print('>>> 屏幕坐标配置信息已存储.')
            self.width = abs(self.scr_pos2[0] - self.scr_pos1[0])
            self.height = abs(self.scr_pos2[1] - self.scr_pos1[1])
            print('------------')

        # ===== position info: =====
        self.area = {
            'menu': (0.8158, 0.875, 0.9677, 0.92),
            'startMission': (0.8254, 0.6608, 0.8901, 0.7257)
        }
        self.img = {
            'menu': self.grab(self.area['menu'], 'arknights_menu'),
            'startMission': None
        }

    def grab(self, float_pos, fname=None, to_PIL=False):
        '''
        Args:
        ------
        - float_pos: position tuple of target area, should be floats from 0~1.
        - fname=None: file name to save.
        - to_PIL=False: Only set `True` when: on linux using `autopy` and need a PIL jpg image.
        '''
        float_x1, float_y1, float_x2, float_y2 = float_pos
        # 开了屏幕缩放的话，记得传参scale！
        x1, y1 = self._set(float_x1, float_y1, scale=SCALE)
        x2, y2 = self._set(float_x2, float_y2,  scale=SCALE)
        return ScreenShot(x1, y1, x2, y2, to_PIL=to_PIL, fname=fname)

    def monitor_cursor_pos(self):
        while 1:
            x, y = self.c.get_pos()
            if self.scr_pos2[0] > x > self.scr_pos1[0] and self.scr_pos2[1] > y > self.scr_pos1[1]:
                x = (x-self.scr_pos1[0])/self.width
                y = (y-self.scr_pos1[1])/self.height
                pos = (round(x, 4), round(y, 4))
            else:
                pos = 'Not in Arknights.'
            info('Float pos: {}, real: {}'.format(pos, self.c.get_pos()))
            time.sleep(0.5)

    def _set(self, float_x, float_y, scale=False):
        '''
        float_x, float_y: float position on the WINDOW.
        scale: scale factor, type: int, >1
        reurn the real position on the screen.
        '''
        x = int(self.scr_pos1[0]+self.width*float_x)
        y = int(self.scr_pos1[1]+self.height*float_y)
        if scale:
            x = int(x / scale)
            y = int(y / scale)
        return x, y

    def click(self, float_x, float_y, sleep_time):
        x, y = self._set(float_x, float_y, scale=False)
        self.c.click((x, y))
        time.sleep(sleep_time)

    def enter_battle(self, supNo=8):
        # [init by yourself]
        enter_team_pos = (0.8959, 0.905)
        mission_start_pos = (0.8685, 0.7975)

        info('行动开始，转移控制权到代理指挥')
        
        if CURRENT_EPOCH == 1:
            self.click(*enter_team_pos, 3)
            self.img['startMission'] = self.grab(self.area['startMission'])
        else:
            self.click(*enter_team_pos, 1)
            if self._monitor('startMission', 5, sleep=False) != -1:
                pass
            else:
                self.click(*mission_start_pos, 1.5)       # 这里博士可能需要嗑药了，磕个药
                self.click(*enter_team_pos, 1)
                if self._monitor('startMission', 5, sleep=False) != -1:
                    pass
                else:
                    logging.error('Running out of time [10s].')
                    os._exit(0)
                
        info('编队结束，行动小队正在前往战场...')
        for _ in range(3):
            self.click(*mission_start_pos, 1)
        info('战斗开始，代理指挥PRTS控制中.')

    def _similar(self, img1, img2, bound=30):
        # to find if 2 imgs(PIL jpg format) are very similar.
        # - bound: if 2 imgs' distance in RGB < bound, return True.
        c1 = np.array(img1).mean(axis=(0, 1))
        c2 = np.array(img2).mean(axis=(0, 1))
        d = np.linalg.norm(c1 - c2)
        # if DEBUG:
        #     print('distance:', d)
        # d +0.0001 to avoid that d == 0
        return d+0.0001 if d < bound else False

    def _monitor(self, names, max_time, sleep, bound=30, AllowPause=False, ClickToSkip=False, EchoError=True):
        '''
        used for monitoring area change.
        When `self.pre_img[name]` is similar to now_img, save now img_bitmap as new img and return.
        If already saved, When `self.img[name]` == now_img, return value.

        Args:
        ------
        - names: tuple, choose from self.area.keys()
        - max_time: maxtime to wait for.
        - sleep: sleep time when use `_similar()` to judge. To avoid the situation: _similar(now, ori) == True but now != ori, because `now_img` is still in randering, they are similar but not the same.
        - bound: if 2 imgs' RGB distance < bound, they are similar.
        - AllowPause: if allow pausing during the loop.
        - ClickToSkip: Click the screen to skip something.
        - EchoError: If printing error message when running out of time.
        '''
        if SYSTEM != 'linux':
            AllowPause = False
        names = (names, ) if len(names[0]) == 1 else names
        beg = time.time()
        pause_time = 0      # set for not calculating time for pause
        flag = 0
        # start monitor:
        while 1:
            for name in names:
                # First running for `name`:
                if not self.img[name]:
                    now, now_bit = self.grab(self.area[name], to_PIL=True)

                    now_bit.save('./debug/{}.png'.format(name))
                    d = self._similar(self.LoadImg[name], now, bound)
                    if d:
                        if sleep:
                            time.sleep(sleep)
                            self._monitor(name, 1.5, 0, bound)
                        else:
                            self.img[name] = now_bit
                            logging.info(
                                'Got new img: {}, Distance: {:.4f}'.format(name, d))
                        return names.index(name)

                # already have self.img[name]:
                elif self.grab(self.area[name], to_PIL=False) == self.img[name]:
                    logging.info('{} Detected, Status change.'.format(name))
                    return names.index(name)

            # run out of time:
            if time.time() - beg - pause_time > max_time:
                if EchoError:
                    logging.error(
                        '{} running out of time: {}s'.format(names, max_time))
                return -1
            # every unit time pass:
            if ClickToSkip and flag == int(CLICK_BREAK_TIME/0.1):
                self.click(0.98, 0.36, 0)
                flag = 0
            flag += 1
            time.sleep(0.1)

    def one_battle(self, go_on=False):
        self.enter_battle()
        # for _ in range(ONE_BATTLE_TIMEOUT):
        #     if self.grab(self.area['menu']) == self.img['menu']:
        #         info(f'行动阶段[{CURRENT_EPOCH}]结束，战略资源获取')
        #         return 1
        #     self.click(0.98, 0.5, 0)

        if self._monitor('menu', ONE_BATTLE_TIMEOUT, sleep=False, ClickToSkip=True) != -1:
            info(f'行动阶段[{CURRENT_EPOCH}]结束，战略资源获取')
        else:
            logging.error('连接超时，与罗德岛断开神经连接')
            os._exit(0)
            

    def run(self):
        info('欢迎回来，博士。')
        beg = time.time()
        for j in range(EPOCH):
            print('\n ----- EPOCH{} START -----'.format(j+1))
            global CURRENT_EPOCH
            CURRENT_EPOCH += 1
            self.one_battle()
            time.sleep(0.5)
        end = time.time()
        logging.info('TotalTime: {:.1f}(min), <{:.1f}(min) on avarage.>'.format(
            (end-beg)/60, (end-beg)/(60*EPOCH)))
        if OPT.shutdown and SYSTEM == 'linux':
            info('任务结束，罗德岛主机即将关闭')
            os.system('shutdown 0')

    def debug(self):
        self.grab(self.area['menu'], 'menu_sample')


if __name__ == '__main__':
    # if debug for pyscreenshot, set level to `INFO`, can't run in `DEBUG` level.
    get_log()
    arknights = Arknights()
    if DEBUG:
        arknights.debug()
    elif OPT.locate:
        arknights.monitor_cursor_pos()
    else:
        arknights.run()
