
# coding: utf-8

# In[2]:


# [TODO] 
# - 游戏结束判定
# - 使用感知哈希智能出牌
# - 每天首次魔力棱镜判定
# - 进入战斗加载判定 （采样attack）
# - 战斗过场动画判定  （采样attack）
# - 体力不足判定    （感知哈希 or ai识别）   ...好像也可以进入战斗的时候等系统提示再嗑果

import win32api, win32con, win32gui, win32ui
import PIL
import time
from config import *
import numpy as np
from utils import compare_img, pic_shot, getColor, echo_info


# In[3]:


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


# In[14]:


class Fgo(object):
    def __init__(self, full_screen=True, sleep=True):
        # [init by yourself] put cursor at the down-right position of the game window.
        
        if full_screen:
            self.height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            self.width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            self.scr_pos1 = (0, 0)
            self.scr_pos2 = (self.width, self.height)
            self.c = Cursor(init_pos=False)
            for x in range(5):
                echo_info('INFO', 
                          'Program will start in %d s, Please enter FULL SCREEN MODE.' % (5-x))
                time.sleep(1)
            
        else:
            self.c = Cursor(init_pos=False)
            while 1:
                in1 = input('[INFO {}] Move cursor to the top-left cornor of Fgo screen, and press ENTER(enter q to exit):'.format(
                    time.strftime('%H:%M:%S')))
                if in1 == 'q':
                    exit()
                self.scr_pos1 = self.c.get_pos()
                echo_info('INFO', 
                          'Get cursor at {}'.format(self.scr_pos1))
                
                in2 = input('[INFO {}] Move cursor to the down-right cornor of Fgo screen, and press ENTER(enter q to exit):'.format(
                    time.strftime('%H:%M:%S')))
                if in2 == 'q':
                    exit()
                self.scr_pos2 = self.c.get_pos()
                echo_info('INFO', 
                          'Get cursor at {}'.format(self.scr_pos2))
                
                res = input('[INFO {}] Continue?[y/n](y to continue, n to reset cursor):'.format(
                    time.strftime('%H:%M:%S')))
                if res == 'n':
                    continue
                else: 
                    break
            if sleep:
                for x in range(3):
                    echo_info('INFO', 
                          'Program will start in %d s, make sure the game window not covered.' % (5-x))
                    time.sleep(1)

            self.width = abs(self.scr_pos2[0] - self.scr_pos1[0])
            self.height = abs(self.scr_pos2[1] - self.scr_pos1[1])
        
        
        #---------------------sampled pix info-----------------------
        # postion of samples:
        self.sample1_x = 0.8854
        self.sample1_y = 0.7824
        self.sample1_RGB = np.array([0, 0, 0])
        
        print('\n---------------------[init over]---------------------------')
        #print('[DEBUG {}] Window width(x) = {}, height(y) = {}'.format(
        #    time.strftime('%H:%M:%S'), self.width, self.height))
        
    
    def _set(self, float_x, float_y):
        # input type: float
        # reurn the real position on the screen.
        return int(self.scr_pos1[0]+self.width*float_x), int(self.scr_pos1[1]+self.height*float_y)
    
    
    def click_act(self, float_x, float_y, sleep_time, click=True):
        pos = self._set(float_x, float_y)
        self.c.move_to(pos)
        if click:
            self.c.click()
        echo_info('INFO', 
                 'simulate click at position: {}'.format(pos))
        time.sleep(sleep_time)
        
    
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
        
        self.click_act(sup_ico_x, sup_ico_y, 0.5)
        self.click_act(sup_tag_x, sup_tag_y, 1.3)
        
        # game start
        # postion of `mission start` tag
        start_x = 0.9281
        start_y = 0.9398
        self.click_act(start_x, start_y, 1)
        
        
    def compare_RGB(self, target, x, y):
        '''
        - x, y: position of pix in Fgo window .
        - target: a numpy array of target RGB value.
        '''
        pass
    
        
    def use_skill(self, skills):
        # position of skills:
        ski_x = [0.0542, 0.1276, 0.2010, 0.3021, 0.3745, 0.4469, 0.5521, 0.6234, 0.6958]
        ski_y = 0.8009
        # snap = 0.0734
        for i in skills:
            # SKILL_SLEEP_TIME = 0.8
            self.click_act(ski_x[i], ski_y, 3)
              
        
    def attack(self):
        # attack icon position:
        atk_ico_x = 0.8823
        atk_ico_y = 0.8444
        self.click_act(atk_ico_x, atk_ico_y, 1)
        
        # use atk card:
        # use ultimate atk card:
        if USE_ULTIMATE:
            # ultimate card position:
            ult_x = [0.3171, 0.5005, 0.6839]
            ult_y = 0.2833
            for x in ult_x:
                self.click_act(x, ult_y, 0.2)
        
        # use normal atk card:
        # normal atk card position:
        atk_card_x = [0.1003+0.2007*x for x in range(5)]
        atk_card_y = 0.7019
        for i in range(3):
            self.click_act(atk_card_x[i], atk_card_y, 0.2)
            
            
    def surveil(self, x1, y1, x2, y2, name=None, save_img=False):
        last_img = self.pic_shot_float(x1, y1, x2, y2)
        last_diff = 0
        for i in range(100):
            beg = time.time()      
            time.sleep(1)
            if save_img:
                img = self.pic_shot_float(x1, y1, x2, y2)
                img.save('./data/{}_{}.jpg'.format(name, i))
            
            now_diff = compare_img(img, last_img)
            print('[DEBUG] now_diff={}, last_diff={}'.format(now_diff, last_diff))
            if now_diff > 5 and now_diff > last_diff:
                echo_info('SURVEIL', 'Detected status change.')
                return 1
            last_diff = now_diff
            last_img = img
            end = time.time()
            print('[SURVEIL {}] Surveiling in area {}, Time use: {}'.format(
                time.strftime('%H:%M:%S'), name, end-beg))
            
            # click the center of screen to skip something.
            # self.click_act(0.5, 0.5, 0) 
        return -1
    
    
    def pic_shot_float(self, float_x1, float_y1, float_x2, float_y2, name=None):
        # error: 关闭屏幕缩放！关闭屏幕缩放！
        x1, y1 = self._set(float_x1, float_y1)
        #self.click_act(x1, y1, 1)
        x2, y2 = self._set(float_x2, float_y2)
        # self.click_act(x2, y2, 1)
        return pic_shot(x1, y1, x2, y2, name)
        
    
    def wait_loading(self):
        self.loading_img = './data/loading.jpg'
        self.atk_img = './data/atk_ico.jpg'
        real_atk = PIL.Image.open(self.atk_img)
        real_loading = PIL.Image.open(self.loading_img)
        
        # sample1 area of attack icon:
        smp1_x1 = 0.8708
        smp1_y1 = 0.7556
        smp1_x2 = 0.8979
        smp1_y2 = 0.8009

        for _ in range(100):
            now_atk_img = self.pic_shot_float(smp1_x1, smp1_y1, smp1_x2, smp1_y2)
            echo_info('TRY', 'detecting satus changing...')
            diff1 = compare_img(now_atk_img, real_atk)
            diff2 = compare_img(now_atk_img, real_loading)
            
            # print('[DEBUG] different between now and ATK is:', diff1)
            # print('[DEBUG] different between now and LOADING is:', diff2)
            if diff1 < diff2 and diff1 < 5:
                time.sleep(0.8)
                echo_info('INFO', 'Detected status change.')
                return 1
            time.sleep(1)
        return -1
    
        
    def one_turn(self):
        # Trun number position: (1298, 123), (1335, 164)
        turn_num_x1 = 0.6760
        turn_num_y1 = 0.1139
        turn_num_x2 = 0.6953
        turn_num_y2 = 0.1519
        
        # self.use_skill(USED_SKILL)
        self.attack()
        
        res = self.surveil(turn_num_x1, turn_num_y1, turn_num_x2, turn_num_y2, name='[TURN_NUMBER]', save_img=False)
        if res == -1:
            echo_info('ERROR', 
                  'Can\'t detected status changing, somethin error, please reboot the program.')
            exit()
        
        
    def run(self):
        self.enter_battle(SUPPORT)
        res = self.wait_loading()
        if res == -1:
            echo_info('ERROR', 
                  'Can\'t detected status changing, somethin error, please reboot the program.')
            exit()
        else:
            self.use_skill(USED_SKILL)
            for i in range(30):
                echo_info('INFO', 'Start turn {}'.format(i))
                self.one_turn()
            
        

        


# In[11]:


fgo = Fgo(full_screen=False, sleep=False)
fgo.run()
# res = fgo.surveil(turn_num_x1, turn_num_y1, turn_num_x2, turn_num_y2, name='[TURN_NUMBER]', save_img=True)
# a = fgo.pic_shot_float(turn_num_x1, turn_num_y1, turn_num_x2, turn_num_y2)
# a.save('a.jpg')


# In[13]:


x, y = (1335, 164)
x/1920, y/1080

