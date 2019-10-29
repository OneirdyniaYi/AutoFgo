# coding: utf-8
# author: Why
# version: 5.0.2
import argparse
import os
import sys
import smtplib
import string
import time
from email import encoders
from email.header import Header
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.mime.text import MIMEText
from collections.abc import Iterable
from ocrApi import img2str
import numpy as np
from PIL import Image
from config import *
from email_config import *

SYSTEM = sys.platform

if SYSTEM == 'linux':
    print('*'*20)
    print('>>> Current system: Linux')
    from utils_linux import *
else:
    from utils_win import *

# ===== Config: =====
CURRENT_EPOCH = 0
END_AFTER_THIS_EPOCH = False
PRE_BREAK_TIME = CLICK_BREAK_TIME
Args = argparse.ArgumentParser()
Args.add_argument('--epoch', '-e', type=int, default=3,
                  help='Num of running battles.')

Args.add_argument('--support', '-s', type=str, default='7',
                  help='ID or name (e.g. `sab` for saber, program will AutoComplete the name) of support servent. ServentID: 0. all,  1. saber,  2. archer,  3. lancer,  4. rider,  5. caster,  6. assassin,  7. berserker,  8. special')

Args.add_argument('--skill', '-S', type=str, default='+',
                  help='Skills you want to set. e.g: `S+12345` for only using 1~5, `S-123` for only NOT using skill 1~3, `S-` for not using any skill, `S+` for using all skills.')

Args.add_argument('--ultimate', '-u', type=str, default='123',
                  help='Ultimate Skills you want to use. exmaple: `u12` for using 1~2, `u-` for NOT using anyone.')

Args.add_argument('--order', '-o', type=int, choices=range(-3, 4), default=0,
                  help='Attacking orders. `n` for attacking `n`th enemy first; `-n` for attacking `n`th enemy first and others in reverse order; 0 for ignoring settings. 1, 2, 3 from RIGHT to LEFT.')

Args.add_argument('--keep', '-k', type=int,
                  help='if 0: keep the window-position same as the last time; if n: load from file n')

Args.add_argument('--clearAP', '-C', type=int, default=0,
                  help='If clear all AP. -Cn to represent: One apple can run n battles. for example, full AP = 125, AP cost by one battle = 40, then n = 3. set 0 for not clearing AP.')

Args.add_argument('--OCR', '-O', action='store_true',
                  help='Use OCR to help attacking. I recommend you use it in some difficult battles.')

Args.add_argument('--no_focus', '-nf', action='store_true',
                  help='Don\'t make cursor focus on Fgo window. You should turn this on when you want to do other things while running fgo.')

Args.add_argument('--CheckPos', '-p', action='store_true',
                  help='To see the window-position, shoud be used with `--keep`.')
Args.add_argument('--debug', '-d', action='store_true',
                  help='Enter DEBUG mode.')
Args.add_argument('--shutdown', '-sd', action='store_true',
                  help='close the simulator after running.')
Args.add_argument('--ContinueRun', '-c', action='store_true',
                  help='Continue running in a battle.')
Args.add_argument('--locate', '-l', action='store_true',
                  help='Monitor cursor\'s  position.')
OPT = Args.parse_args()


# ===== Global varibles: =====
KEEP_POSITION = OPT.keep if OPT.keep != None else False
SEND_MAIL = False if OPT.epoch < 5 or OPT.debug else True


# ===== Main Code: =====
def update_var():
    if OPT.shutdown and SYSTEM == 'linux':
        input(
            '\033[1;31m>>> [Warning] Your PC will shutdown after running. Continue?\033[0m')
    if OPT.debug:
        print('>>> [Attention] You are in DEBUG Mode!')

    # Parse OPT.skill and OPT.ultimate:
    if OPT.skill:
        if OPT.skill[0] in ('+', '-'):
            for x in OPT.skill[1:]:
                if x not in '123456789':
                    print('[Error] `Skill` args format error, try again.')
                    os._exit(0)
            if OPT.skill[1:] == '':
                OPT.skill = tuple(range(1, 10)) if OPT.skill[0] == '+' else ()
            elif OPT.skill[0] == '+':
                OPT.skill = tuple([int(x) for x in OPT.skill[1:]])
            else:
                OPT.skill = tuple({x for x in range(1, 10)} -
                                  set([int(x) for x in OPT.skill[1:]]))
        else:
            print('[Error] Args <skill> format error, try again.')
            os._exit(0)
    if OPT.ultimate:
        if OPT.ultimate == '-':
            OPT.ultimate = ()
        else:
            for x in OPT.ultimate:
                if x not in '123':
                    print('[Error] Args <ultimate> format error, try again.')
                    os._exit(0)
            OPT.ultimate = tuple([int(x) for x in OPT.ultimate])

    # Parse OPT.support:
    try:
        OPT.support = int(OPT.support)
        if OPT.support not in tuple(range(9)):
            print('[Error] Args <Support> format error, try again.')
            os._exit(0)
    except:
        supportID = ('all', 'saber', 'archer', 'lancer', 'rider',
                     'caster', 'assassin', 'berserker', 'special')

        res = [OPT.support in x for x in supportID]
        if res.count(True) != 1:
            print('[Error] Args <Support> format error, try again.')
            os._exit(0)
        else:
            OPT.support = res.index(True)


def info(str):
    logging.info('<E{}/{}> - {}'.format(CURRENT_EPOCH, OPT.epoch, str))


class DigitFinder:
    def __init__(self, keep=string.digits):
        self.comp = dict((ord(c), c) for c in keep)

    def __getitem__(self, k):
        return self.comp.get(k)


class Fgo:
    __slots__ = ('c', 'width', 'height', 'scr_pos1',
                 'scr_pos2', 'area', 'img', 'LoadImg', 'skill_used_turn', 'digitFinder')

    def __init__(self, full_screen=True, sleep=True):
        # [init by yourself] put cursor at the down-right position of the game window.
        self.c = Cursor(init_pos=False)
        self.digitFinder = DigitFinder()
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
                    print('>>> Running keeping last position.')
                elif KEEP_POSITION:
                    print('>>> Load init_pos from file', KEEP_POSITION)
            else:
                while 1:
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

                    res = input('Continue? [y(continue) /n(reset) /q(quit)]:')
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
                    print('>>> Position info saved.')
            self.width = abs(self.scr_pos2[0] - self.scr_pos1[0])
            self.height = abs(self.scr_pos2[1] - self.scr_pos1[1])
            print('*'*20)

        # ===== position info: =====
        self.area = {
            'menu': (0.0693, 0.7889, 0.1297, 0.8917),       # avator position
            'StartMission': (0.8984, 0.9352, 0.9542, 0.9630),
            'AP_recover': (0.2511, 0.177, 0.2907, 0.2464),
            # 'support': (0.6257, 0.1558, 0.6803, 0.1997),
            'atk': (0.8708, 0.7556, 0.8979, 0.8009),
            # 'fufu': (0.4611, 0.9694, 0.4731, 0.9907)
            'fufu': (0.5088, 0.8926, 0.53, 0.999)
        }
        self.img = {
            'menu': None,
            'StartMission': None,
            'AP_recover': None,
            'atk': None,
            # 'nero': None,
            'fufu': None,
            'skills': list(range(9))
        }
        # load sample imgs:
        self.LoadImg = {x: Image.open(
            ROOT + 'data/{}_sample.png'.format(x)) for x in self.area.keys()}
        if not OPT.ContinueRun and not OPT.debug and not OPT.locate:
            if self._monitor('menu', 3, 0) == -1:
                os._exit(0)

    def grab(self, float_pos, fname=None, to_PIL=False):
        '''
        Args:
        ------
        * float_pos: position tuple of target area, should be floats from 0~1, or name in `self.area`
        * fname=None: file name to save.
        * to_PIL=False: Only set `True` when: on linux using `autopy` and need a PIL jpg image.
        '''
        if type(float_pos) == str:
            float_pos = self.area[float_pos]

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
                pos = 'Not in Fgo.'
            info('Float pos: {}, real: {}'.format(pos, self.c.get_pos()))
            time.sleep(0.5)

    def _set(self, float_x, float_y, scale=False):
        '''
        * float_x, float_y: float position on the WINDOW.
        * scale: scale factor, type: int, >1
        * reurn the real position on the screen.
        '''
        x = int(self.scr_pos1[0]+self.width*float_x)
        y = int(self.scr_pos1[1]+self.height*float_y)
        if scale:
            x = int(x / scale)
            y = int(y / scale)
        return x, y

    def click(self, float_x, float_y, sleep_time):
        x, y = self._set(float_x, float_y, scale=False)
        bak_x, bak_y = self.c.get_pos()
        self.c.click((x, y))
        if OPT.no_focus:
            # click the original position to make cursor focus on your jobs:
            self.c.click((bak_x, bak_y))
        else:
            # just move back:
            self.c.move_to((bak_x, bak_y))
        time.sleep(sleep_time)

    def send_mail(self, status):
        # status: 'err' or 'done'
        self.grab((0, 0, 1, 1), 'final_shot')
        with open(ROOT + 'data/fgo.LOG', 'r') as f:
            res = f.readlines()
            res = [x.replace('<', '&lt;').replace('>', '&gt;') for x in res]
            res = ''.join([x[:-1]+'<br />' for x in res])
        msg = MIMEMultipart()
        with open(ROOT + 'data/final_shot.png', 'rb') as f:
            mime = MIMEBase('image', 'jpg', filename='shot.png')
            mime.add_header('Content-Disposition',
                            'attachment', filename='shot.png')
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            mime.set_payload(f.read())
            encoders.encode_base64(mime)
            msg.attach(mime)

        msg.attach(MIMEText('<html><body><p><img src="cid:0"></p>' +
                            '<font size=\"1\">{}</font>'.format(res) +
                            '</body></html>', 'html', 'utf-8'))
        msg['From'] = Header('why酱のFGO脚本', 'utf-8')
        msg['Subject'] = Header(
            '[FGO] - Status: {}, {}'.format(status, time.strftime('%m-%d%H:%M')), 'utf-8')
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        try:
            server.ehlo()
            # server.starttls()
            server.login(FROM_ADDRESS, PASSWD)
            server.sendmail(FROM_ADDRESS, [TO_ADDRESS], msg.as_string())
            server.quit()
            print('>>> Mail sent successfully. Please check it.')
        except Exception as e:
            print('\nError type: ', e)
            print('>>> Mail sent failed. Maybe there are something wrong.')

    def _mission_start(self):
        # postion of `mission start` tag
        for _ in range(3):
            self.click(0.9398, 0.9281, 1)
        if CHOOSE_ITEM:
            # using the first item:
            # self.click(0.5, 0.2866, 0.5)
            # self.click(0.6478, 0.7819, 0.5)

            # not using item:
            self.click(0.6469, 0.9131, 0.5)

    def enter_battle(self, supNo=8):
        # [init by yourself] put the tag of battle at the top of screen.
        # postion of support servant tag.
        sup_tag_x = 0.4893
        sup_tag_y = 0.3944
        # click to hide the terminal:
        # if CURRENT_EPOCH == 1:
        #     self.click(0.2828, 0.7435, 0.3)

        # click the center of battle tag.
        # self.click(0.7252, 0.2740, 2)
        self.click(0.7252, 0.2740, 0)
        self.use_apple()
        # choose support servent class icon:
        # time.sleep(EXTRA_SLEEP_UNIT*4)
        # if CURRENT_EPOCH == 1:
        #     time.sleep(1.5)
        self.click(0.0729+0.0527*supNo, 0.1796, 1)
        self.click(sup_tag_x, sup_tag_y, 1)

        # if self._monitor('StartMission', 10, 0.3) != -1:
        # no screenshot bugs, change to:
        if True:
            time.sleep(1)
            self._mission_start()
            return 0
        else:
            self.click(sup_tag_x, sup_tag_y, 1)
            if not(self._similar(self.grab(self.area['StartMission'], to_PIL=True)[0], self.img['StartMission'])):
                logging.error('Can\'t get START_MISSION tag for 10s.')
                self.send_mail('Error')
                raise RuntimeError('Can\'t get START_MISSION tag for 10s')

    def get_skill_img(self, turn, saveImg=False):
        # turn = False for get all imgs.
        ski_x = [0.0542, 0.1276, 0.2010, 0.3021,
                 0.3745, 0.4469, 0.5521, 0.6234, 0.6958]
        ski_y = 0.8009
        skill_imgs = list(range(9))
        for no in OPT.skill:
            i = no - 1
            if turn and turn - self.skill_used_turn[i] < SKILL_MIN_CD:
                skill_imgs[i] = self.img['skills'][i]
                continue
            # N = 25 if SYSTEM == 'linux' else 1
            # Screenshot bug (gray block bug) has been fixed. 1 is enough.
            N = 1
            imgs = [self.grab((ski_x[i]-0.0138, ski_y-0.0222,
                               ski_x[i]+0.0138, ski_y)) for _ in range(N)]
            img = imgs[0]
            max_count = imgs.count(imgs[0])
            for x in imgs:
                count = imgs.count(x)
                if count > max_count:
                    img = x
                    max_count = count
            # skill_imgs[i] = self.grab(
            #     (ski_x[i]-0.0138, ski_y-0.0222, ski_x[i]+0.0138, ski_y))
            skill_imgs[i] = img
            if saveImg:
                skill_imgs[i].save('./debug/{}.png'.format(i))
        return skill_imgs

    def _use_one_skill(self, turn, skill_ix):
        ski_x = [0.0542, 0.1276, 0.2010, 0.3021,
                 0.3745, 0.4469, 0.5521, 0.6234, 0.6958]    # ski_y = 0.8009
        # if not (skill_ix == 7 and turn == 1):
        self.click(ski_x[skill_ix], 0.8009, SKILL_SLEEP1)
        self.click(0.5, 0.5, SKILL_SLEEP2)
        self.click(0.6978, 0.0267, SKILL_SLEEP3)
        # To see if skill is really used.
        beg = time.time()
        click_status = True
        while not(self.grab(self.area['atk']) == self.img['atk']):
            # to avoid clicking avator:
            if click_status and not int(time.time() - beg) % 0.5:
                # time.sleep(0.5)
                self.click(0.6978, 0.0267, 0)
                click_status = False
            if 8 > time.time() - beg > 6:
                logging.warning('Click avator wrongly,auto-fixed.')
                self.click(0.6978, 0.0267, 0.5)
            if time.time() - beg > 8:
                return -1
        # atk disappeared for over 1s, using skill succes:
        if time.time() - beg > 1:
            self.skill_used_turn[skill_ix] = turn
        return 1

    def use_skill(self, turn):
        # position of skills:
        info('Now using skills...')
        # snap_x = 0.0734
        if turn == 1:
            time.sleep(EXTRA_SLEEP_UNIT*10)
            self.skill_used_turn = [None for _ in range(9)]
            for no in OPT.skill:
                self._use_one_skill(turn, no-1)
                self.skill_used_turn[no-1] = 1
            if YILI:
                self._use_one_skill(turn, 6)
            time.sleep(EXTRA_SLEEP_UNIT*2)
            # first turn, get imgs of all skills
            self.img['skills'] = self.get_skill_img(turn=False)
        else:
            info('Skill CD: {}'.format(
                [turn-x for x in self.skill_used_turn if type(x) == int]))
            time.sleep(EXTRA_SLEEP_UNIT*4)
            # only get imgs for skills that not in CD(now_turn - used_turn > min_CD):
            now_skill_img = self.get_skill_img(turn)
            if not(now_skill_img == self.img['skills']):
                time.sleep(EXTRA_SLEEP_UNIT*10)
                for no in OPT.skill:
                    if not(now_skill_img[no-1] == self.img['skills'][no-1]):
                        self._use_one_skill(turn, no-1)
                    if turn == 2 and no == 8:
                        self._use_one_skill(turn, no-1)
                if YILI:
                    self._use_one_skill(turn, 6)
                time.sleep(EXTRA_SLEEP_UNIT*2)
                self.img['skills'] = self.get_skill_img(turn=False)

    def _choose_card(self):
        # normal atk card position:
        # for `ix` in range(-2, 3), card in No 1~5, get the screenshot for each card and calculate the mean of RGB values.
        if SYSTEM == 'linux':
            pics = [self.grab((0.4411+ix*0.2015, 0.7333, 0.5588+ix *
                               0.2015, 0.8324), to_PIL=True)[0] for ix in range(-2, 3)]
        else:
            pics = [self.grab((0.4411+ix*0.2015, 0.7333, 0.5588+ix *
                               0.2015, 0.8324)) for ix in range(-2, 3)]
        RGBs = [np.array(x).mean(axis=(0, 1)) for x in pics]
        nearest3RGB = [None, None, None]
        min_sigma = 1e5
        for j in range(5):
            for i in range(j):
                cards = set(range(5)) - {i, j}
                now = np.array([RGBs[x] for x in cards]).var(axis=0).sum()
                # print('> {}: Var: {}'.format(cards, now))
                if now < min_sigma:
                    min_sigma = now
                    nearest3RGB = cards
        logging.info('MinVar=Var{}={:.1f}.'.format(
            nearest3RGB, min_sigma))
        # print(nearest3RGB)
        return tuple(nearest3RGB), min_sigma

    def attack(self):
        if OPT.OCR:
            try:
                enemyHP, ourHP = self.ocrHP()
            except Exception as e:
                print(e)
                logging.error('OCR failed, please check images in `./data`')
            else:
                if enemyHP < 50000 and ourHP > 24000:
                    OPT.ultimate = ()

        info('Now start attacking....')
        # click attack icon:
        # time.sleep(EXTRA_SLEEP_UNIT*5)
        self.click(0.8823, 0.8444, 1)
        while self._monitor('atk', 0.1, 0, EchoError=False) != -1:
            logging.warning('Click ATK_Icon failed.')
            self.click(0.8823, 0.8444, 1)
        # use normal atk card:
        atk_card_x = [0.1003+0.2007*x for x in range(5)]
        nearest3ix, min_sigma = self._choose_card()
        sigmas = [min_sigma]
        ixs = [nearest3ix]
        if min_sigma > 300 and SYSTEM == 'linux':
            for _ in range(2):
                nearest3ix, min_sigma = self._choose_card()
                sigmas.append(min_sigma)
                ixs.append(nearest3ix)
                if min_sigma < 300:
                    break
            if min_sigma > 300:
                min_sigma = min(sigmas)
                nearest3ix = ixs[sigmas.index(min_sigma)]
        logging.info('CardUse:{}, MinVar(RGB)={:.1f}.'.format(
            nearest3ix, min_sigma))
        # time.sleep(EXTRA_SLEEP_UNIT*3)
        for i in range(3):
            self.click(atk_card_x[nearest3ix[i]], 0.7019, ATK_SLEEP_TIME)
            if i == 0 and OPT.ultimate:
                time.sleep(0.2)
                ult_x = [0.3171, 0.5005, 0.6839]
                for j in OPT.ultimate:
                    # j = 1, 2, 3
                    self.click(ult_x[j-1], 0.2833, ULTIMATE_SLEEP)
        # To avoid `Can't use card` status:
        for _ in range(1):
            for i in range(5):
                self.click(atk_card_x[i], 0.7019, 0.2)
            time.sleep(1)
        info('Card using over.')

    def _similar(self, img1, img2, bound=30):
        # to find if 2 imgs(PIL jpg format) are very similar.
        # - bound: if 2 imgs' distance in RGB < bound, return True.
        c1 = np.array(img1).mean(axis=(0, 1))
        c2 = np.array(img2).mean(axis=(0, 1))
        d = np.linalg.norm(c1 - c2)
        # if OPT.debug:

        # info(f'distance: {d}')
        # d +0.0001 to avoid that d == 0
        return d+0.0001 if d < bound else False

    def _monitor(self, names, max_time, sleep, bound=30, AllowListenKey=False, ClickToSkip=False, EchoError=True):
        '''
        used for monitoring area change.
        When `self.pre_img[name]` is similar to now_img, save now img_bitmap as new img and return.
        If already saved, When `self.img[name]` == now_img, return value.

        Args:
        ------
        * names: tuple, choose from self.area.keys()
        * max_time: maxtime to wait for.
        * sleep: sleep time when use `_similar()` to judge. To avoid the situation: _similar(now, ori) == True but now != ori, because `now_img` is still in randering, they are similar but not the same.
        * bound: if 2 imgs' RGB distance < bound, they are similar.
        * AllowListenKey: allow keyboard listening during the loop (for pause & end).
        * ClickToSkip: Click the screen to skip something.
        * EchoError: If printing error message when running out of time.
        '''
        if SYSTEM != 'linux':
            AllowListenKey = False
        names = (names, ) if len(names[0]) == 1 else names
        beg = time.time()
        pause_time = 0      # set for not calculating time for pause
        flag = 0
        if AllowListenKey:
            kb_listener = KeyEventListener()
            kb_listener.start()
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

            # to listen keyboard and pause:
            if AllowListenKey and KeyEventListener.PAUSE:
                break_time = time.time()
                input(
                    '\033[5;37;40m >>> Press enter to continue running: \033[0m')
                KeyEventListener.PAUSE = False
                pause_time += (time.time() - break_time)
            elif AllowListenKey and KeyEventListener.LAST_EPOCH:
                global END_AFTER_THIS_EPOCH
                END_AFTER_THIS_EPOCH = True
            # run out of time:
            if time.time() - beg - pause_time > max_time:
                if EchoError:
                    logging.error(
                        '{} running out of time: {}s'.format(names, max_time))
                return -1
            # every unit time pass:
            if ClickToSkip and flag == int(CLICK_BREAK_TIME/0.1):
                self.click(0.7771, 0.9627, 0)
                flag = 0
            flag += 1
            time.sleep(0.1)

    def wait_loading(self):
        logging.info('<LOAD> - Now loading...')
        if CURRENT_EPOCH == 1:
            if FUFU_NOT_DETECTED:
                time.sleep(10)
                self.img['fufu'] = self.grab('fufu')
                info('ATTENTION: Now saved sample for `fufu` since monitor failed.')
            else:
                self._monitor('fufu', 30, 0.5, 10)
        if self._monitor('atk', 150, 0.5) == -1:
            os._exit(0)
        info('Finish loading, battle start.')

    def one_turn(self, turn):
        # Define functions to react each kinds of changes DURING a turn:
        def atk():
            info('Got status change, Start new turn.')
            return 'NEXT_TURN'

        def fufu():
            global CLICK_BREAK_TIME
            CLICK_BREAK_TIME = 5
            info('Get loading page, end epoch{}.'.format(CURRENT_EPOCH))
            time.sleep(1)
            return 'CONTINUE'

        def menu():
            info('Detected change, battle finish.')
            global PRE_BREAK_TIME, CLICK_BREAK_TIME
            CLICK_BREAK_TIME = PRE_BREAK_TIME
            return 'BATTLE_OVER'

        self.use_skill(turn)
        # reset the attack order:
        if OPT.order:
            # AtkOrder[OPT.order] represent the atk order.
            AtkOrder = (None, (0, 1, 2),
                        (0, 2, 1), (1, 2, 0),
                        (2, 1, 0), (2, 0, 1),
                        (1, 0, 2))
            # position: 0, 1, 2 from left to right.
            enemy_x = (0.1010, 0.3010, 0.4901)
            for ix in AtkOrder[OPT.order]:
                self.click(enemy_x[ix], 0.0602, CLICK_BAR_SLEEP)
        self.attack()
        time.sleep(1.5)

        # Monitoring status change:
        info('Monitoring, no change got...')
        res = self._monitor(('atk', 'fufu', 'menu'), 60, 0, 20, True, True)
        if res == -1:
            atk_card_x = [0.1003+0.2007*x for x in range(5)]
            for _ in range(3):
                self.click(0.6978, 0.0267, 1)
            for i in range(5):
                self.click(atk_card_x[i], 0.7019, 0.2)
            logging.warning('Something wrong. Trying to fix it.')
            res = self._monitor(('atk', 'fufu', 'menu'), 50, 0, 20, True, True)
        if res != -1:
            status = (atk, fufu, menu)[res]()
            if status == 'CONTINUE':
                res = self._monitor(('atk', 'menu'), 50, 0, 20, False, True)
                status = (atk, menu)[res]()
            return status
        else:
            logging.error(
                'Running out of time for 170s.')
            self.send_mail('Error')
            raise RuntimeError('Running out of time.')

    def one_battle(self, go_on=False):
        if not go_on:
            self.enter_battle(OPT.support)
            # wait for going into loading page:
            self.wait_loading()
        # ContinueRun:
        elif not self.img['atk']:
            if self._monitor('atk', 3, 0) == -1:
                os._exit(0)

        for i in range(50):
            info('Start Turn {}'.format(i+1))
            # Here CD_num == i
            status = self.one_turn(i+1)
            if status == 'BATTLE_OVER':
                return 1

        logging.error('Running over 50 turns, program was forced to stop.')
        self.send_mail('Error')
        raise RuntimeError(
            'Running over 50 turns, program was forced to stop.')

    def use_apple(self):
        # if self.grab(self.area['AP_recover']) == self.img['AP_recover']:
        if self._monitor('AP_recover', 1.5, 0.2, EchoError=False, bound=15) != -1:
            logging.info('>>> Using apple...')
            # choose apple:
            self.click(0.5, 0.4463, 0.7)
            self.click(0.5, 0.6473, 0.7)
            # choose OK:
            self.click(0.6563, 0.7824, 1)
            logging.info('>>> Apple using over.')
            time.sleep(1.5)
            global CURRENT_EPOCH

            one_apple_battle_num = OPT.clearAP  # go to see `OPT.clearAP` help msg
            if OPT.epoch - CURRENT_EPOCH < one_apple_battle_num - 1 and OPT.clearAP:
                OPT.epoch = CURRENT_EPOCH + one_apple_battle_num - 1
                logging.info(
                    'Auto change EPOCH to {} to use all AP.'.format(OPT.epoch))

    def save_AP_recover_img(self):
        # choose AP bar:
        self.click(0.1896, 0.9611, 1)
        if self._monitor('AP_recover', 3, 0.2) == -1:
            os._exit(0)
        # click `exit`
        self.click(0.5, 0.8630, 0.5)

    def ocrHP(self):
        '''
        monitor HP of enemy and servent, using BaiduOCR API.
        '''
        enemy_x = (0.0852, 0.2756, 0.4654)
        our_x = (0.1545, 0.4015, 0.65)
        enemy_y = 0.04
        our_y = 0.85

        w = 0.1
        h = 0.055

        enemyHP = 0
        ourHP = 0
        for i in range(3):
            def getHP(i, x, y, name):
                self.grab((x, y, x + w, y+h), f'{name}HP_{i}')
                res = img2str(
                    ROOT + f'data/{name}HP_{i}.png').translate(self.digitFinder)
                return int(res) if res != '' else 0

            hp1 = getHP(i, enemy_x[i], enemy_y, 'enemy')
            hp2 = getHP(i, our_x[i], our_y, 'our')

            enemyHP += hp1
            ourHP += hp2
            info(f'OCR [{i+1}] enemyHP: {hp1}, ourHP: {hp2}.')

        info(f'OCR [all] enemyHP: {enemyHP}, ourHP: {ourHP} on total.')
        return enemyHP, ourHP

    def run(self):
        beg = time.time()
        # if not self.img['AP_recover']:
        # self.save_AP_recover_img()
        for j in range(OPT.epoch):
            print('\n ----- EPOCH{} START -----'.format(j+1))
            global CURRENT_EPOCH
            CURRENT_EPOCH += 1
            self.one_battle()
            time.sleep(0.5)

            # Stop manually:
            if END_AFTER_THIS_EPOCH:
                print('>>> [Info] Manual Interruption after epoch {}.'.format(
                    CURRENT_EPOCH))
                os._exit(0)

        end = time.time()
        logging.info('TotalTime: {:.1f}(min), <{:.1f}(min) on avarage.>'.format(
            (end-beg)/60, (end-beg)/(60*OPT.epoch)))
        if OPT.shutdown and SYSTEM == 'linux':
            # k = PyKeyboard()
            # k.press_keys(['Control_L', 'Delete'])
            self.send_mail('Done')
            os.system('shutdown 0')

        if SEND_MAIL:
            self.send_mail('Done')

    def debug(self):
        # while 1:
        #     self.c.click(self.c.get_pos())
        #     time.sleep(0.1)
        # self.run()
        self.grab(self.area['fufu'], 'fufu_sample')
        # self.ocrHP()


if __name__ == '__main__':
    # if you want to debug for pyscreenshot, set level to `INFO`. Script can't run in `DEBUG` level.
    update_var()
    get_log()
    fgo = Fgo(full_screen=FULL_SCREEN, sleep=False)
    if OPT.debug:
        fgo.debug()
    elif OPT.locate:
        fgo.monitor_cursor_pos()
    elif OPT.ContinueRun:
        fgo.one_battle(go_on=True)
    else:
        fgo.run()
