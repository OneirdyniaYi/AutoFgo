# coding: utf-8
# author: Why
import argparse
import logging
import os
import sys
import smtplib
import time
from email import encoders
from email.header import Header
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
from PIL import Image
from config import *

SYSTEM = sys.platform

if SYSTEM == 'linux':
    print('>>> Current system: Linux')
    from utils_linux import *
else:
    from utils_win import *

# ===== Config: =====
CURRENT_EPOCH = 0
PRE_BREAK_TIME = CLICK_BREAK_TIME
Args = argparse.ArgumentParser()
Args.add_argument('--epoch', '-e', type=int, help='Num of running battles.')
Args.add_argument('--support', '-s', type=int, help='ID of support servent.')
Args.add_argument('--order', '-o', type=int, choices=range(-3, 4), default=0,
                  help='Attacking orders. `n` for attacking `n`th enemy first; `-n` for attacking `n`th enemy first and others in reverse order; 0 for ignoring settings.')
Args.add_argument('--keep', '-k', action='store_true',
                  help='To keep the window-position same as the last time.')
Args.add_argument('--fromFile', '-f', action='store_true',
                  help='Load self.img from files. You should use this mode with `--keep` option.')
Args.add_argument('--debug', '-d', action='store_true',
                  help='Enter DEBUG mode.')
Args.add_argument('--ContinueRun', '-c', action='store_true',
                  help='Continue running in a battle.')
Args.add_argument('--locate', '-l', action='store_true',
                  help='Monitor cursor\'s  position.')
OPT = Args.parse_args()

global DEBUG, EPOCH, SUPPORT, SEND_MAIL, CONTINUE_RUN
DEBUG = OPT.debug if OPT.debug else DEBUG
EPOCH = OPT.epoch if OPT.epoch else EPOCH
SUPPORT = OPT.support if OPT.support else SUPPORT
CONTINUE_RUN = True if OPT.ContinueRun else CONTINUE_RUN
SEND_MAIL = False if EPOCH < 5 or DEBUG else SEND_MAIL
print('>>> Attention: You are in DEBUG Mode now!' if DEBUG else '')
# ===== Main Code: =====


def get_log():
    fmt = '> %(asctime)s:%(levelname)s - %(message)s'
    # date_fmt_echo = '%m-%d %H:%M:%S'
    date_fmt_file = '%H:%M'
    logging.basicConfig(level=logging.DEBUG, format=fmt,
                        datefmt=date_fmt_file, filename=ROOT + 'data/fgo.LOG', filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    if DEBUG:
        console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(fmt, datefmt=date_fmt_file))
    logging.getLogger().addHandler(console)


class Fgo(object):
    __slots__ = ('c', 'width', 'height', 'scr_pos1',
                 'scr_pos2', 'area_pos', 'img')

    def __init__(self, full_screen=True, sleep=True):
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
            if OPT.keep:
                with open(ROOT + 'data/INIT_POS', 'r') as f:
                    res = f.readlines()
                res = tuple([int(x) for x in res[0].split(' ')])
                self.scr_pos1 = res[:2]
                self.scr_pos2 = res[2:]
                print('>>> Continue running keeping last position.')
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
                with open(ROOT + 'data/INIT_POS', 'w') as f:
                    pos = str(self.scr_pos1[0]) + ' ' + str(self.scr_pos1[1]) + \
                        ' ' + str(self.scr_pos2[0]) + \
                        ' ' + str(self.scr_pos2[1])
                    f.write(pos)
                    print('>>> Position info saved.')
            self.width = abs(self.scr_pos2[0] - self.scr_pos1[0])
            self.height = abs(self.scr_pos2[1] - self.scr_pos1[1])

        # ===== position info: =====
        self.area_pos = {
            'menu': (0.0693, 0.7889, 0.1297, 0.8917),       # avator position
            'StartMission': (0.8984, 0.9352, 0.9542, 0.9630),
            'AP_recover': (0.2511, 0.177, 0.2907, 0.2464),
            # 'support': (0.6257, 0.1558, 0.6803, 0.1997),
            'nero': (0.3726, 0.381, 0.4458, 0.5225),
            'AtkIcon': (0.8708, 0.7556, 0.8979, 0.8009),
            'fufu': (0.4167, 0.9260, 0.4427, 1)
            # 'fufu': (0.4167, 0.9260, 0.4427, 0.963)
        }
        self.img = {
            'menu': None,
            'StartMission': None,
            'AP_recover': None,
            'AtkIcon': None,
            'nero': None,
            'fufu': None,
            'skills': list(range(9))
        }
        self._save_img('menu')
        if OPT.keep and OPT.fromFile:
            self._load_last_img()

    def _load_last_img(self):
        root = ROOT + 'data/'
        ignore = ('menu', 'nero', 'skills')
        for name in self.img.keys():
            fp = root + name + '.png'
            if os.path.exists(fp) and name not in ignore:
                self.img[name] = Image.open(fp)
            else:
                logging.warn('File {}.png not found.'.format(name))

    def _save_img(self, name, save_file=False):
        if DEBUG or SAVE_IMG:
            save_file = True
        # self.img[name] = self.getImg(name)
        self.img[name] = self.grab(
            self.area_pos[name], fname=(name if save_file else None))
        return self.img[name]

    def getImg(self, name):
        return self.grab(self.area_pos[name])

    def monitor_cursor_pos(self):
        while 1:
            x, y = self.c.get_pos()
            if self.scr_pos2[0] > x > self.scr_pos1[0] and self.scr_pos2[1] > y > self.scr_pos1[1]:
                x = (x-self.scr_pos1[0])/self.width
                y = (y-self.scr_pos1[1])/self.height
                pos = (round(x, 4), round(y, 4))
            else:
                pos = 'Not in Fgo.'
            logging.info(
                '<M{}/{}> Float pos: {}, real: {}'.format(CURRENT_EPOCH, EPOCH, pos, self.c.get_pos()))
            time.sleep(0.5)

    def _set(self, float_x, float_y):
        # input type: float
        # reurn the real position on the screen.
        return int(self.scr_pos1[0]+self.width*float_x), int(self.scr_pos1[1]+self.height*float_y)

    def click_act(self, float_x, float_y, sleep_time):
        pos = self._set(float_x, float_y)
        if SYSTEM == 'linux':
            self.c.click(pos)
        else:
            self.c.move_to(pos)
            self.c.click()
        time.sleep(sleep_time)

    def send_mail(self, status):
        # status: 'err' or 'done'
        self.grab((0, 0, 1, 1), 'final_shot')
        with open(ROOT + 'data/fgo.LOG', 'r') as f:
            res = f.readlines()
            res = [x.replace('<', '&lt;') for x in res]
            res = [x.replace('>', '&gt;') for x in res]
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
        msg['From'] = Header('why酱的FGO脚本', 'utf-8')
        msg['Subject'] = Header('<FGO {}> Running Stop <STATUS:{}>'.format(
            time.strftime('%m-%d|%H:%M'), status), 'utf-8')
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
        self.click_act(0.9398, 0.9281, 1)
        if Choose_item:
            self.click_act(0.5, 0.2866, 0.5)
            self.click_act(0.6478, 0.7819, 0.5)
            # self.click_act(0.6469, 0.9131, 0.5)

    def enter_battle(self, supNo=8):
        # [init by yourself] put the tag of battle at the top of screen.
        # postion of support servant tag.
        sup_tag_x = 0.4893
        sup_tag_y = 0.3944
        # click the center of battle tag.
        self.click_act(0.7252, 0.2740, 1)
        self.use_apple()
        # choose support servent class icon:
        time.sleep(EXTRA_SLEEP_UNIT*5)
        self.click_act(0.0729+0.0527*supNo, 0.1796, 0.8)
        self.click_act(sup_tag_x, sup_tag_y, 1)

        if not self.img['StartMission']:
            self._save_img('StartMission')
            time.sleep(EXTRA_SLEEP_UNIT*10)
            self._mission_start()
        else:
            time1 = time.time()
            while 1:
                if self.getImg('StartMission') == self.img['StartMission']:
                    self._mission_start()
                    return 0

                elif time.time() - time1 > 10:
                    self.click_act(sup_tag_x, sup_tag_y, 1)
                    if not(self.getImg('StartMission') == self.img['StartMission']):
                        logging.error(
                            '<M{}/{}> - Can\'t get START_MISSION tag for 10s.'.format(CURRENT_EPOCH, EPOCH))
                        self.send_mail('Error')
                        raise RuntimeError(
                            'Can\'t get START_MISSION tag for 10s')

    def get_skill_img(self):
        ski_x = [0.0542, 0.1276, 0.2010, 0.3021,
                 0.3745, 0.4469, 0.5521, 0.6234, 0.6958]
        ski_y = 0.8009
        skill_imgs = list(range(9))
        for i in USED_SKILL:
            skill_imgs[i] = self.grab(
                (ski_x[i]-0.0138, ski_y-0.0222, ski_x[i]+0.0138, ski_y))
            skill_imgs[i].save(ROOT+ 'data/{}.png'.format(i))
        return skill_imgs

    def _use_one_skill(self, skill_no):
        flag = 1
        ski_x = [0.0542, 0.1276, 0.2010, 0.3021,
                 0.3745, 0.4469, 0.5521, 0.6234, 0.6958]    # ski_y = 0.8009
        self.click_act(ski_x[skill_no], 0.8009, SKILL_SLEEP1)
        self.click_act(0.5, 0.5, SKILL_SLEEP2)
        self.click_act(0.0521, 0.4259, SKILL_SLEEP3)
        # To see if skill is really used.
        beg = time.time()
        while not(self.getImg('AtkIcon') == self.img['AtkIcon']):
            if 6 > time.time() - beg > 5:
                logging.warning('Click avator wrongly,auto-fixed.')
                self.click_act(0.0521, 0.4259, 0.2)
                flag = -1
            if time.time() - beg > 6:
                return flag
        return flag

    def use_skill(self, turn):
        # position of skills:
        logging.info(
            '<E{}/{}> - Now using skills...'.format(CURRENT_EPOCH, EPOCH))
        # snap = 0.0734
        if turn == 1:
            for i in USED_SKILL:
                self._use_one_skill(i)
            if Yili:
                # 小伊丽的三技能...
                self._use_one_skill(6)
            self.img['skills'] = self.get_skill_img()
        else:
            time.sleep(EXTRA_SLEEP_UNIT*3)
            now_skill_img = self.get_skill_img()
            if not(now_skill_img == self.img['skills']):
                for i in USED_SKILL:
                    if not(now_skill_img[i] == self.img['skills'][i]):
                        self._use_one_skill(i)
                if Yili:
                    # 小伊丽的三技能...
                    self._use_one_skill(6)
                self.img['skills'] = self.get_skill_img()

    def _choose_card(self):
        # normal atk card position:
        # for `ix` in range(-2, 3), card in No 1~5, get the screenshot for each card and calculate the mean of RGB values.
        autopy_to_PIL = True if SYSTEM == 'linux' else False
        pics = [self.grab((0.4411+ix*0.2015, 0.7333, 0.5588+ix *
                           0.2015, 0.8324), autopy_to_PIL=autopy_to_PIL) for ix in range(-2, 3)]
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
        logging.info('Choose card: {}, Min var(RGB)={:.1f}.'.format(
            nearest3RGB, min_sigma))
        # print(nearest3RGB)
        return tuple(nearest3RGB)

    def attack(self):
        logging.info(
            '<E{}/{}> - Now start attacking....'.format(CURRENT_EPOCH, EPOCH))
        # click attack icon:
        time.sleep(EXTRA_SLEEP_UNIT*5)
        self.click_act(0.8823, 0.8444, 1)
        # use normal atk card:
        atk_card_x = [0.1003+0.2007*x for x in range(5)]
        nearest3ix = self._choose_card()
        for i in range(3):
            self.click_act(atk_card_x[nearest3ix[i]], 0.7019, ATK_SLEEP_TIME)
            if i == 0 and USED_ULTIMATE:
                # logging.info('>>> Using Utimate skills...')
                time.sleep(0.2)
                ult_x = [0.3171, 0.5005, 0.6839]
                for j in USED_ULTIMATE:
                    self.click_act(ult_x[j], 0.2833, ULTIMATE_SLEEP)
        # To avoid `Can't use card` status:
        for i in range(5):
            self.click_act(atk_card_x[i], 0.7019, 0.1)
        logging.info(
            '<E{}/{}> - ATK Card using over.'.format(CURRENT_EPOCH, EPOCH))

    def grab(self, float_pos, fname=None, autopy_to_PIL=False):
        '''
        Args:
        ------
        - float_pos: position tuple of target area, should be floats from 0~1.
        - fname=None: file name to save.
        - autopy_to_PIL=False: Only set `True` when on linux using `autopy`, and need to return a PIL image.
        '''
        float_x1, float_y1, float_x2, float_y2 = float_pos
        # Windows error: 关闭屏幕缩放！关闭屏幕缩放！
        x1, y1 = self._set(float_x1, float_y1)
        x2, y2 = self._set(float_x2, float_y2)
        if autopy_to_PIL:
            img = ScreenShot(x1, y1, x2, y2, to_PIL=True)
        else:
            img = ScreenShot(x1, y1, x2, y2)
        if fname:
            img.save(ROOT + 'data/{}.png'.format(fname))
        return img

    def _similar(self, img1, img2):
        # to find if 2 imgs(PIL jpg format) are very similar.
        c1 = np.array(img1).mean(axis=(0, 1))
        c2 = np.array(img2).mean(axis=(0, 1))
        return True if np.linalg.norm(c1 - c2) < 30 else False
        # print('> Distance:', d)

    def wait_loading(self):
        time.sleep(LOADING_WAIT_TIME)
        # loading_img = self.getImg('AtkIcon')
        logging.info('<LOAD> - Monitoring, Now loading...')
        if not self.img['fufu']:
            self._save_img('fufu')
        sample_AtkIco = Image.open(ROOT + 'data/atk_ico.jpg')
        for _ in range(100):
            # when first running and got changed:
            # the following `not(a == b)` was for autopy on linux
            # there eill be bug if set `a!=b` directly.

            now_AtkIco = self.grab(self.area_pos['AtkIcon'], autopy_to_PIL= True)
            if not self.img['AtkIcon'] and self._similar(now_AtkIco, sample_AtkIco):
            # if not self.img['AtkIcon'] and not(self.getImg('fufu') == self.img['fufu']):
                logging.info('<LOAD> - Get status change, finish loading.')
                self.img['AtkIcon'] = now_AtkIco
                self.img['AtkIcon'].save(ROOT+ 'data/atk.png')
                for _ in range(3):
                    self.click_act(0.7771, 0.9627, 1)
                return 0
            elif self.img['AtkIcon'] and self.getImg('AtkIcon') == self.img['AtkIcon']:
                logging.info('<LOAD> - Get status change, finish loading.')
                return 0
            else:
                time.sleep(WAIT_LOADING_SLEEP)
        logging.error('Connection timeout. Check your network.')
        self.send_mail('Err')
        raise RuntimeError('Connection timeout in loading.')

    def _react_change(self, name):
        '''
        Define functions to react each kinds of changes during a turn.
        function foramt: `def name():` means a function when self.img['name'] was detected.
        '''
        def nero():
            if Nero_MAX:
                self.click_act(0.3485, 0.7947, 0.5)
                logging.warning(
                    '<M{}/{}> - Entered wrong battle, auto-fixed. battle finish.'.format(CURRENT_EPOCH, EPOCH))
                return 'BATTLE_OVER'

        def AtkIcon():
            logging.info(
                '<M{}/{}> - Got status change, Start new turn...'.format(CURRENT_EPOCH, EPOCH))
            return 'NEXT_TURN'

        def fufu():
            logging.info(
                '<M{}/{}> - Enter loading, battle finish.'.format(CURRENT_EPOCH, EPOCH))
            global CLICK_BREAK_TIME
            CLICK_BREAK_TIME = 3.5
            logging.info(
                '<M{}/{}> - Get loading page, end epoch{}.'.format(CURRENT_EPOCH, EPOCH, CURRENT_EPOCH))
            time.sleep(1)
            return 'CONTINUE'

        def menu():
            logging.info(
                '<M{}/{}> - Detected change, battle finish.'.format(CURRENT_EPOCH, EPOCH))
            global PRE_BREAK_TIME, CLICK_BREAK_TIME
            CLICK_BREAK_TIME = PRE_BREAK_TIME
            return 'BATTLE_OVER'

        react_func = {
            'nero': nero,
            'AtkIcon': AtkIcon,
            'fufu': fufu,
            'menu': menu
        }
        if self.img[name] and self.getImg(name) == self.img[name]:
            return react_func[name]()
        else:
            return 0    # no match.

    def one_turn_new(self, turn):
        # update saved atk icon:
        if not self.img['AtkIcon']:
            self._save_img('AtkIcon')
        if USE_SKILL:
            self.use_skill(turn)
        # reset the attack order:
        if OPT.order:
            # AtkOrder[OPT.order] represent the atk order.
            AtkOrder = (None, (0, 1, 2),
                        (1, 0, 2), (2, 0, 1),
                        (2, 1, 0), (1, 2, 0),
                        (0, 2, 1))
            enemy_x = (0.1010, 0.3010, 0.4901)
            for ix in AtkOrder[OPT.order]:
                self.click_act(enemy_x[ix], 0.0602, CLICK_BAR_SLEEP)
        self.attack()
        time.sleep(1.5)

        # Monitoring status change:
        beg_time = time.time()
        j = 0
        while 1:
            if 35 > time.time() - beg_time > 30:
                self.click_act(0.0521, 0.4259, 1)
                logging.warning('Something wrong. Trying to fix it.')
            elif time.time() - beg_time > 150:
                logging.error(
                    'Running out of time, No status change detected for 2min30s.')
                self.send_mail('Err')
                raise RuntimeError('Running out of time.')
            monitor_ob = ('nero', 'AtkIcon', 'fufu', 'menu')
            if Nero_MAX:
                monitor_ob.append('nero')
            for x in monitor_ob:
                res = self._react_change(x)
                if res == 'CONTINUE':
                    break
                elif res:   # `battle_over` or `next_turn`
                    return res
            # click to skip something
            self.click_act(0.7771, 0.9627, CLICK_BREAK_TIME)

            if not j:
                logging.info(
                    '<M{}/{}> - Monitoring, no change got...'.format(CURRENT_EPOCH, EPOCH))
            j += 1

    def one_battle(self, go_on=False):
        if not go_on:
            self.enter_battle(SUPPORT)
            # wait for going into loading page:
            self.wait_loading()
        # ContinueRun:
        elif not self.img['AtkIcon']:
            self._save_img('AtkIcon')

        for i in range(50):
            logging.info(
                '<E{}/{}> - Start Turn {}'.format(CURRENT_EPOCH, EPOCH, i+1))
            # Here CD_num == i
            status = self.one_turn_new(i+1)
            if Nero_MAX:
                time.sleep(0.5)
                if self.getImg('nero') == self.img['nero']:
                    self.click_act(0.3485, 0.7947, 0.5)
                    logging.warning(
                        '<M{}/{}> - Entered wrong battle, auto-fixed. battle finish.'.format(CURRENT_EPOCH, EPOCH))
            if status == 'BATTLE_OVER':
                return 1

        logging.error('Running over 50 turns, program was forced to stop.')
        self.send_mail('Err')
        raise RuntimeError(
            'Running over 50 turns, program was forced to stop.')

    def use_apple(self):
        if self.getImg('AP_recover') == self.img['AP_recover']:
            logging.info('>>> Using apple...')
            # choose apple:
            self.click_act(0.5, 0.4463, 0.7)
            self.click_act(0.5, 0.6473, 0.7)
            # choose OK:
            self.click_act(0.6563, 0.7824, 1)
            logging.info('>>> Apple using over.')
            time.sleep(1.5)
            global EPOCH, CURRENT_EPOCH
            if EPOCH - CURRENT_EPOCH < ONE_APPLE_BATTLE - 1 and CLEAR_AP:
                EPOCH = CURRENT_EPOCH + ONE_APPLE_BATTLE - 1
                logging.info(
                    'Auto change EPOCH to {} to use all AP.'.format(EPOCH))

    def clear_data(self):
        files = os.listdir(ROOT + 'data')
        ignore = ['atk_ico.png', 'loading.png', 'INIT_POS']
        for x in self.img.keys():
            ignore.append('{}.png'.format(x))
        for x in files:
            if x in ignore:
                continue
            else:
                os.remove(ROOT + 'data/{}'.format(x))

    def save_AP_recover_pic(self):
        print('>>> Saving AP_recover pic...')
        # choose AP bar:
        self.click_act(0.1896, 0.9611, 1)
        self._save_img('AP_recover')
        # click `exit`
        self.click_act(0.5, 0.8630, 0.5)

        if Nero_MAX:
            self.click_act(0.7314, 0.8427, 0.8)
            self._save_img('nero', False)
            self.click_act(0.3485, 0.7947, 0.5)

    def run(self):
        beg = time.time()
        if not self.img['AP_recover']:
            self.save_AP_recover_pic()
        j = 0
        while j < EPOCH:
            print(
                '\n -----<< EPOCH{} START >>-----'.format(j+1))
            global CURRENT_EPOCH
            CURRENT_EPOCH += 1
            self.one_battle()
            time.sleep(0.5)
            j += 1
        end = time.time()
        logging.info('Total time: {:.1f}(min), <{:.1f}(min) on avarage.>'.format(
            (end-beg)/60, (end-beg)/(60*EPOCH)))
        if SEND_MAIL:
            self.send_mail('Done')
        self.clear_data()

    def debug_grab(self):
        ori = self.grab((0, 0, 1, 1))
        ori.save('./debug/ori.png')
        while 1:
            now = self.grab((0, 0, 1, 1))
            now.save('./debug/now.png')
            print('running...')
            if not (now == ori):
                break
            time.sleep(0.1)


if __name__ == '__main__':
    # if debug for pyscreenshot, set level to `INFO`, can't run in `DEBUG` level.
    # get_log()
    fgo = Fgo(full_screen=FULL_SCREEN, sleep=False)
    if DEBUG:
        # fgo.wait_loading()
        
        fgo.debug_grab()
        # fgo._choose_card()
        # img = fgo.grab(fgo.area_pos['fufu'])
        pass
    elif OPT.locate:
        fgo.monitor_cursor_pos()
    elif CONTINUE_RUN:
        fgo.one_battle(go_on=True)
    else:
        fgo.run()
