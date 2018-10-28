
# coding: utf-8

# In[1]:


# [TODO] 
# - 使用感知hash智能出牌

import os 
import win32api, win32con, win32gui, win32ui
import PIL
import time
from config import *
import numpy as np
import logging
from utils import compare_img, pic_shot, compare_img_new
from email.header import Header
import smtplib 
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.mime.text import MIMEText
from email import encoders

SKILL_CD = YOUR_SKILL_CD + (SUPPORT_SKILL_CD, )*3
CURRENT_EPOCH = 0


def get_log():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s - %(levelname)s]: %(message)s', 
                            datefmt='%H:%M:%S', filename='fgo.LOG', filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter('[%(asctime)s - %(levelname)s]: %(message)s', datefmt='%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(console)
# In[2]:


class Cursor(object):
    def __init__(self, init_pos):
        # init_pos：should be a tuple, set `False` to skip initing position.
        if init_pos!=False and len(init_pos)==2:
            self.move_to(init_pos)
    
    def move_to(self, pos):
        win32api.SetCursorPos(pos)
    
    def get_pos(self):
        return win32api.GetCursorPos()
    
    def click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    def right_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0) 
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


class Fgo(object):
    def __init__(self, full_screen=True, sleep=True):
        # [init by yourself] put cursor at the down-right position of the game window.
        self.cal_apple_num()
        logging.info('==> Apple using After {}'.format(self.apple_use_epoch))
        if full_screen:
            self.height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            self.width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            self.scr_pos1 = (0, 0)
            self.scr_pos2 = (self.width, self.height)
            self.c = Cursor(init_pos=False)
            for x in range(5):             
                logging.info('Start in %d s, Please enter FULL SCREEN.' % (5-x))
                time.sleep(1)
                   
        else:
            self.c = Cursor(init_pos=False)
            while 1:
                in1 = input('==> Move cursor to top-left of Fgo, press ENTER (q to exit): ')
                if in1 == 'q':
                    print('==> Running stop')
                    os._exit(0)
                self.scr_pos1 = self.c.get_pos()
                print('==> Get cursor at {}'.format(self.scr_pos1))
                
                in2 = input('==> Move cursor to down-right of Fgo, press ENTER (q to exit): ')
                if in2 == 'q':
                    print('==> Running stop')
                    os._exit(0)
                self.scr_pos2 = self.c.get_pos()
                print('==> Get cursor at {}'.format(self.scr_pos2))
                
                res = input('Continue? [y(continue) /n(reset) /q(quit)]:'.format(
                    time.strftime('%H:%M:%S')))
                if res == 'n':
                    continue
                elif res == 'q':
                    os._exit(0)
                else: 
                    break
            if sleep:
                for x in range(3):
                    logging.info('Start in %d s, make sure the window not covered.' % (3-x))
                    time.sleep(1)
            self.width = abs(self.scr_pos2[0] - self.scr_pos1[0])
            self.height = abs(self.scr_pos2[1] - self.scr_pos1[1])
        #---------------------sampled pix info-----------------------
        # position info, type: 'name': (x1, x2, y1, y2)
        self.area_pos = {
            'menu': (0.0693, 0.7889, 0.1297, 0.8917),
            'StartMission': (0.875, 0.9194, 0.9807, 0.9565), 
            'AP_recover': (0.4583, 0.0556, 0.5391, 0.0926),
            'AtkIcon': (0.8708, 0.7556, 0.8979, 0.8009)
        }   

        # `pre` means this image was saves before code running.
        self.img = {
            'pre_loading': PIL.Image.open('./data/loading.jpg'),
            'pre_atk': PIL.Image.open('./data/atk_ico.jpg'), 
            'menu': self.pic_shot_float(self.area_pos['menu']), 
            'StartMission': None, 
            'AP_recover': None
        }
        # get a screen shot of menu icon:
        self.img['menu'].save('./data/menu.jpg')
        #print('[DEBUG {}] Window width(x) = {}, height(y) = {}'.format(
        #    time.strftime('%H:%M:%S'), self.width, self.height))
    def monitor_cursor_pos(self):
        while 1:
            x, y = self.c.get_pos()
            if self.scr_pos2[0]> x >self.scr_pos1[0] and self.scr_pos2[1]> y >self.scr_pos1[1]:
                x = (x-self.scr_pos1[0])/self.width
                y = (y-self.scr_pos1[1])/self.height
                pos = (round(x, 4), round(y, 4))
            else:
                pos = 'Not in Fgo window.'
            logging.info('<MNTR> Now cursor pos: {}'.format(pos))
            time.sleep(0.5)


    def _set(self, float_x, float_y):
        # input type: float
        # reurn the real position on the screen.
        return int(self.scr_pos1[0]+self.width*float_x), int(self.scr_pos1[1]+self.height*float_y)
    
    def click_act(self, float_x, float_y, sleep_time, click=True, info=True):
        pos = self._set(float_x, float_y)
        self.c.move_to(pos)
        if click:
            try:
                self.c.click()
            except:
                logging.warning('Screen was locked. You can ignore this message.')
                pass
        # if not DEBUG and info:
            # logging.info('<E{}/{}> - Simulate cursor click at {}'.format(CURRENT_EPOCH, EPOCH, (float_x, float_y)))
        time.sleep(sleep_time)
        
        
    def send_mail(self, status):
        '''
        - status: 'err' or 'done'
        '''
        self.pic_shot_float((0, 0, 1, 1), './data/final_shot.jpg')
        with open('fgo.LOG', 'r') as f:
            res = f.readlines()
            res = [x.replace('<', '&lt;') for x in res]
            res = [x.replace('>', '&gt;') for x in res]
            res = ''.join([x[:-1]+'<br />' for x in res])
        msg = MIMEMultipart()
        with open('./data/final_shot.jpg', 'rb') as f:
            mime = MIMEBase('image', 'jpg', filename = 'shot.jpg')
            mime.add_header('Content-Disposition', 'attachment', filename='shot.jpg')
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            mime.set_payload(f.read())
            encoders.encode_base64(mime)
            msg.attach(mime)

        msg.attach(MIMEText('<html><body><p><img src="cid:0"></p>' +
            '<font size=\"1\">{}</font>'.format(res) +
            '</body></html>', 'html', 'utf-8'))
        msg['From'] = Header('why酱的FGO脚本', 'utf-8')
        msg['Subject'] = Header('<FGO {}> Running Stop <STATUS:{}>'.format(time.strftime('%m-%d|%H:%M'), status), 'utf-8')
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        try:
            server.ehlo()
            # server.starttls()
            server.login(FROM_ADDRESS, PASSWD)
            server.sendmail(FROM_ADDRESS, [TO_ADDRESS], msg.as_string())
            server.quit()
            print('==> Mail sent successfully. Please check it.')
        except Exception as e:
            print('\nError type: ', e)
            print('==> Mail sent failed. Maybe there are something wrong.')

    def cal_apple_num(self):
        global EPOCH
        self.apple_use_epoch = []
        global INIT_AP
        if INIT_AP < BATTLE_AP_COST:
            self.apple_use_epoch.append(0)
            INIT_AP += ONE_APPLE_AP
        now_ap = INIT_AP    
        for i in range(EPOCH):
            no = i+1
            now_ap -= BATTLE_AP_COST
            if now_ap < BATTLE_AP_COST and no!=EPOCH:
                self.apple_use_epoch.append(no)
                now_ap += ONE_APPLE_AP
            
        if now_ap > BATTLE_AP_COST:
            print('=====\nNow using apple after epoch: {}'.format(self.apple_use_epoch))
            tmp = EPOCH
            
            while now_ap > BATTLE_AP_COST:
                tmp += 1
                now_ap -= ONE_APPLE_AP
            res = input('You\'d better change epoch to {} to clear all AP. Process?(y/n/q): '.format(tmp))
            if res not in ('n', 'N', 'q'):
                EPOCH = tmp
                print('Now EPOCH = {}\n=====\n'.format(EPOCH))
            elif res == 'q':
                print('==> Code running stop.')
                os._exit(0)


    def enter_battle(self, supNo=8):
        # [init by yourself] put the tag of battle at the top of screen.
        
        # postion of the center of battle tag.
        bat_tag_y = 0.2740
        bat_tag_x = 0.7252
        self.click_act(bat_tag_x, bat_tag_y, 1)
        
        # choose support:
        # postion of support servant tag.
        sup_tag_x = 0.4893
        sup_tag_y = 0.3944
        # postion of support class icon.
        sup_ico_x = 0.0729+0.0527*supNo
        sup_ico_y = 0.1796
        
        self.click_act(sup_ico_x, sup_ico_y, 0.8)
        self.click_act(sup_tag_x, sup_tag_y, 1)

        # save `StartMission icon`
        # postion of `mission start` tag
        start_y = 0.9398
        start_x = 0.9281
        if not self.img['StartMission']:
            self.img['StartMission'] = self.pic_shot_float(self.area_pos['StartMission'])
            self.img['StartMission'].save('./data/StartMission.jpg')
            self.click_act(start_x, start_y, 1)
        else:
            time1 = time.time()
            while 1:
                if self.pic_shot_float(self.area_pos['StartMission']) == self.img['StartMission']:
                    self.click_act(start_x, start_y, 1)
                    return 0
                if time.time() - time1 > 10:
                    logging.error('<MNTR> - Can\'t get START_MISSION tag for 20s.')
                    self.send_mail('Error')
                    raise RuntimeError('Can\'t get START_MISSION tag for 10s')

      
    def use_skill(self, skills, timeout=SKILL_SLEEP_TIME):
        # position of skills:
        logging.info('<E{}/{}> - Now using skills...'.format(CURRENT_EPOCH, EPOCH))
        ski_x = [0.0542, 0.1276, 0.2010, 0.3021, 0.3745, 0.4469, 0.5521, 0.6234, 0.6958]
        ski_y = 0.8009
        # snap = 0.0734
        for i in skills:
            self.click_act(ski_x[i], ski_y, 0.5)
            self.click_act(0.5, 0.5, 0.2)
            self.click_act(0.0521, 0.4259, timeout-0.7)
        logging.info('<E{}/{}> - Skills using over.'.format(CURRENT_EPOCH, EPOCH))

              
    def attack(self):
        logging.info('<E{}/{}> - Now start attacking....'.format(CURRENT_EPOCH, EPOCH))

        # attack icon position:
        atk_ico_x = 0.8823
        atk_ico_y = 0.8444
        self.click_act(atk_ico_x, atk_ico_y, 1)
        
        
        # use normal atk card:
        # normal atk card position:
        atk_card_x = [0.1003+0.2007*x for x in range(5)]
        atk_card_y = 0.7019
        for i in range(3):
            self.click_act(atk_card_x[i], atk_card_y, ATK_SLEEP_TIME)
            if i==0:
                # use atk card:
                # use ultimate atk card:
                if USE_ULTIMATE:
                    # ultimate card position:
                    # logging.info('==> Using Utimate skills...')
                    time.sleep(0.5)
                    ult_x = [0.3171, 0.5005, 0.6839]
                    ult_y = 0.2833
                    for x in ult_x:
                        self.click_act(x, ult_y, 0.1)
        logging.info('<E{}/{}> - ATK Card using over.'.format(CURRENT_EPOCH, EPOCH))

    
    def pic_shot_float(self, pos, name=None):
        float_x1, float_y1, float_x2, float_y2 = pos
        # error: 关闭屏幕缩放！关闭屏幕缩放！
        x1, y1 = self._set(float_x1, float_y1)
        #self.click_act(x1, y1, 1)
        x2, y2 = self._set(float_x2, float_y2)
        # self.click_act(x2, y2, 1)
        return pic_shot(x1, y1, x2, y2, name)
         
    def wait_loading(self, save_img=False, algo=0, sleep=None, mode=0):
        '''
        sample in the attack icon per 1s, if loading process is over, break the loop.
        '''
        real_atk = self.img['pre_atk']
        real_loading = self.img['pre_loading']
        
        for i in range(100):
            now_atk_img = self.pic_shot_float(self.area_pos['AtkIcon'])
            now_atk_img.save('./data/now_loading.jpg')
            if not i:
                logging.info('<LOAD> - Monitoring at area1, Now loading...')
            diff1 = compare_img_new(now_atk_img, real_atk, algo)
            diff2 = compare_img_new(now_atk_img, real_loading, algo)
            
            if DEBUG:
                logging.debug('Diff between now_img and ATK is:', diff1)
                logging.debug('Diff between now_img and LOADING is:', diff2)
            
            if mode == -1:
                condition = (diff2 == 0 and diff1 > 0)
            else:
                condition = (diff1 < diff2 and diff2!=0)
                
            if condition:
                time.sleep(0.8)
                logging.info('<MNTR> - Detected status change, loaded over.')
                return diff1
                if sleep:
                    # wait for background anime finishing:
                    time.sleep(sleep)
            time.sleep(1)
            
        logging.error('Connection timeout. Maybe there are some problems with your network.')
        self.send_mail('Err')
        raise RuntimeError('Connection timeout during loading.')
    
    def cal_diff(self, x1, y1, x2, y2, target, save_img=False, hash=True):
        '''
        sample in the position of attack icon to find that if the game is in the loading page.
        return a BOOL type data.
        - x1, y1, x2, y2: the position of the origin area.
        - save_img: if you want to save images.
        - hash: use hash algorithm or compare image simply. 
        '''        
        real_loading = target
        now_atk_img = self.pic_shot_float((x1, y1, x2, y2))
        if DEBUG:
            now_atk_img.save('./data/sample.jpg')
        if hash:
            return compare_img_new(now_atk_img, real_loading, 0)
        else:
            return 0 if now_atk_img==self.img['pre_atk'] else -1
     
    def cal_atk_diff(self, targrt, save_img=False, hash=True):
        # sample1 area of attack icon:
        smp1_x1, smp1_y1, smp1_x2, smp1_y2 = self.area_pos['AtkIcon']     
        return self.cal_diff(smp1_x1, smp1_y1, smp1_x2, smp1_y2, self.img['pre_atk'], save_img=save_img, hash=hash)
    
        
    def one_turn_new(self):   
        # uodate saved atk icon:
        self.new_atk_img = self.pic_shot_float(self.area_pos['AtkIcon'])
        self.new_atk_img.save('./data/save_new_atk.jpg')
        
        if ATK_BEHIND_FIRST:
            self.click_act(0.3010, 0.0602, 0.1)
            self.click_act(0.1010, 0.0593, 0.1)
        self.attack()
        time.sleep(3)
        
        # Start waiting status change:
        beg_time = time.time()
        # compare atk icon to the last saved icon.
        j = 0
        while 1:
            if time.time() - beg_time > 180:
                logging.error('Running out of time, No status change detected for 3min.')
                self.send_mail('Err')
                raise RuntimeError('Running out of time.')

            now_atk_img = self.pic_shot_float(self.area_pos['AtkIcon'])
            if now_atk_img == self.new_atk_img:
                logging.info('<MNTR> - Got status change, Start new turn...')
                return 0
            else:
                now_menu_img = self.pic_shot_float(self.area_pos['menu'])
                # save for avoid entering the wrong battle.
                now_StartMission_img = self.pic_shot_float(self.area_pos['StartMission'])
                if not self.img['AP_recover']:
                    now_AP_recover_img = self.pic_shot_float(self.area_pos['AP_recover'])

                # now_menu_img.save('./data/now_menu.jpg')
                # now_AP_recover_img.save('./data/now_AP_recover.jpg')
                # now_StartMission_img.save('./data/now_StartMission.jpg')

                if DEBUG:
                    diff = compare_img_new(self.img['menu'], now_menu_img, algo=1)
                    logging.debug('Menu img diff:={}'.format(diff))
                    
                if now_StartMission_img == self.img['StartMission']:
                    self.click_act(0.0766, 0.0565, 1)
                    self.click_act(0.0766, 0.0565, 1)
                    logging.warning('<MNTR> - Entered wrong battle, auto-fixed. battle finish.')
                    return 1
                    # logging.info('EPOCH({}/{}) - No change detected in area1.'.format(CURRENT_EPOCH, EPOCH))
                elif now_AP_recover_img == self.img['AP_recover']:
                    self.click_act(0.5, 0.7843, 0.5)
                    self.click_act(0.5, 0.8620, 0.5)
                    global EPOCH, CURRENT_EPOCH
                    EPOCH = CURRENT_EPOCH + 3
                    logging.warning('Apple use error, auto-fixed. Wrong Apple use: {}'.format(self.apple_use_epoch))
                    logging.warning('init_ap = {}, battle_ap_cost = {}, one+apple_ap = {}'.format(INIT_AP, BATTLE_AP_COST, ONE_APPLE_AP))
                    self.apple_use_epoch = ()
                
                if now_menu_img  == self.img['menu']:
                    logging.info('<MNTR> - Detected status changing, battle finish.')
                    return 1
                else:
                    self.click_act(0.7771, 0.9627, 0.8, info=False)
                    # click to skip something
                    # self.click_act(0.7771, 0.9370, 1)
                    if not j:
                        logging.info('<MNTR> - Monitoring (0.7771, 0.9627), no change...')
                    j += 1
                    # time.sleep(SURVEIL_TIME_OUT)
                
    def reuse_skill(self, cd_num):
        skills = []
        for i in range(len(SKILL_CD)):
            if SKILL_CD[i] == cd_num:
                skills.append(i)
        if len(skills):
            time.sleep(0.2)
            self.use_skill(skills, timeout=SKILL_SLEEP_TIME)
            return 1
        else:
            return 0    
    

    def one_battle(self, go_on=False):
        '''
        main part of running the program. 
        '''
        if not go_on:
            self.enter_battle(SUPPORT)
            # wait for going into loading page:
            time.sleep(3.5)
            self.diff_atk = self.wait_loading(save_img=DEBUG, sleep=5.5)
            if USE_SKILL:
                time.sleep(0.2)
                self.use_skill(USED_SKILL, timeout=SKILL_SLEEP_TIME)
            else:
                time.sleep(2)
        
        for i in range(50):
            logging.info('<E{}/{}> - Start Turn {}'.format(CURRENT_EPOCH, EPOCH, i+1))
            
            # Here CD_num == i
            if USE_SKILL:
                self.reuse_skill(i)
                time.sleep(1)
            over = self.one_turn_new()    
            if over:
                return 1
        logging.error('Running over 50 turns, program was forced to stop.')
        self.send_mail('Err')
        raise RuntimeError('Running over 50 turns, program was forced to stop.')
        

    def use_apple(self, num):
        '''
        use apple AFTER the `num`th epoch.
        '''
        USE_APPLE = True
        if USE_APPLE and num in self.apple_use_epoch:
            logging.info('==> Using apple...')
            # choose AP bar:
            self.click_act(0.1896, 0.9611, 0.7)
            # choose apple:
            self.click_act(0.5, 0.4463, 0.7)
            # get shot:
            if not self.img['AP_recover']:
                self.img['AP_recover'] = self.pic_shot_float(self.area_pos['AP_recover'])
            # choose OK:
            self.click_act(0.6563, 0.7824, 1)
            logging.info('==> Apple using over.')

    def clear_data(self):
        files = os.listdir('./data')
        for x in files:
            if x == 'atk_ico.jpg' or 'loading.jpg':
                continue
            else:
                os.remove('./data/{}'.format(x))

    def run(self):
        beg = time.time()
        self.use_apple(0)
        for j in range(EPOCH):
            print('\n----------------------< Battle EPOCH{} Start >----------------------'.format(j+1))
            global CURRENT_EPOCH
            CURRENT_EPOCH += 1
            self.one_battle() 
            self.use_apple(j+1)
            # between battles:
            time.sleep(1)
        end = time.time()
        logging.info('Everything done, Total time use: {:.1f}min, <{:.1f}min on avarage.>'.format((end-beg)/60, (end-beg)/(60*EPOCH)))
        self.send_mail('Done')
        self.clear_data()
        


# In[4]:


if __name__ == '__main__':
    get_log()
    fgo = Fgo(full_screen=FULL_SCREEN, sleep=False)
    #fgo.one_battle(go_on=True)
    # fgo.use_skill((1, 2))
    # fgo.send_mail('test')
    # fgo.monitor_cursor_pos()
    fgo.run()


# In[ ]:


# x, y = (133, 852)
# x/1920, y/1080

