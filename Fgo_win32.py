
# coding: utf-8

# In[1]:


# [TODO] 
# - 使用感知hash智能出牌

import win32api, win32con, win32gui, win32ui
import PIL
import time
from config import *
import numpy as np
from utils import compare_img, pic_shot, compare_RGB, echo_info, compare_img_new
SKILL_CD = YOUR_SKILL_CD + (SUPPORT_SKILL_CD, )*3


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


# In[3]:


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
                          'Program will start in %d s, make sure the game window not covered.' % (3-x))
                    time.sleep(1)

            self.width = abs(self.scr_pos2[0] - self.scr_pos1[0])
            self.height = abs(self.scr_pos2[1] - self.scr_pos1[1])
        
        
        #---------------------sampled pix info-----------------------
        self.loading_img = PIL.Image.open('./data/loading.jpg')
        self.atk_img = PIL.Image.open('./data/atk_ico.jpg')
        
        # menu position: (1710, 1005), (1850, 1057)
        self.menu_x1 = 0.8906
        self.menu_y1 = 0.9306
        self.menu_x2 = 0.9635
        self.menu_y2 = 0.9787
        
        # get a screen shot of menu icon:
        self.menu_img = self.pic_shot_float(self.menu_x1, self.menu_y1, self.menu_x2, self.menu_y2)
        if DEBUG:
            self.menu_img.save('./data/menu.jpg')
        
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
            try:
                self.c.click()
            except:
                echo_info('ERROR', 'Screen locked. You can ignore this message.')
                pass
        if not DEBUG:
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
    
        
    def use_skill(self, skills, timeout=SKILL_SLEEP_TIME):
        # position of skills:
        echo_info('START', 'Now using skills...')
        ski_x = [0.0542, 0.1276, 0.2010, 0.3021, 0.3745, 0.4469, 0.5521, 0.6234, 0.6958]
        ski_y = 0.8009
        # snap = 0.0734
        for i in skills:
            self.click_act(ski_x[i], ski_y, timeout)
              
        
    def attack(self):
        echo_info('INFO', 'Start attacking...')
        # attack icon position:
        atk_ico_x = 0.8823
        atk_ico_y = 0.8444
        self.click_act(atk_ico_x, atk_ico_y, 1)
        
        # use atk card:
        # use ultimate atk card:
        if USE_ULTIMATE:
            # ultimate card position:
            time.sleep(0.5)
            ult_x = [0.3171, 0.5005, 0.6839]
            ult_y = 0.2833
            for x in ult_x:
                self.click_act(x, ult_y, 0.1)
        
        # use normal atk card:
        # normal atk card position:
        atk_card_x = [0.1003+0.2007*x for x in range(5)]
        atk_card_y = 0.7019
        for i in range(3):
            self.click_act(atk_card_x[i], atk_card_y, 0.1)
            
            
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
        return -1
    
    
    def pic_shot_float(self, float_x1, float_y1, float_x2, float_y2, name=None):
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
        real_atk = self.atk_img
        real_loading = self.loading_img
        
        # sample1 area of attack icon:
        smp1_x1 = 0.8708
        smp1_y1 = 0.7556
        smp1_x2 = 0.8979
        smp1_y2 = 0.8009
        
        for i in range(100):
            now_atk_img = self.pic_shot_float(smp1_x1, smp1_y1, smp1_x2, smp1_y2)
            if save_img:
                now_atk_img.save('./data/now_loading_{}.jpg'.format(i))
            echo_info('INFO', 'Waiting for loading...Surveil in area sample 1.')
            diff1 = compare_img_new(now_atk_img, real_atk, algo)
            diff2 = compare_img_new(now_atk_img, real_loading, algo)
            
            if DEBUG:
                print('[DEBUG] diff between now_img and ATK is:', diff1)
                print('[DEBUG] diff between now_img and LOADING is:', diff2)
            
            if mode == -1:
                condition = (diff2 == 0 and diff1 > 0)
            else:
                condition = (diff1 < diff2 and diff2!=0)
                
            if condition:
                time.sleep(0.8)
                echo_info('INFO', 'Detected status change.')
                return diff1
                if sleep:
                    # wait for background anime finishing:
                    time.sleep(sleep)
            time.sleep(1)
            
        echo_info('ERROR', 'Connection timeout. Maybe there are some problems with your network.')
        return -1
    
    
    def cal_diff(self, x1, y1, x2, y2, target, save_img=False, hash=True):
        '''
        sample in the position of attack icon to find that if the game is in the loading page.
        return a BOOL type data.
        - x1, y1, x2, y2: the position of the origin area.
        - save_img: if you want to save images.
        - hash: use hash algorithm or compare image simply. 
        '''        
        real_loading = target
        now_atk_img = self.pic_shot_float(x1, y1, x2, y2)
        if save_img:
            now_atk_img.save('./data/sample.jpg')
        if hash:
            return compare_img_new(now_atk_img, real_loading, 0)
        else:
            return 0 if now_atk_img==self.atk_img else -1
        
    
    def cal_atk_diff(self, targrt, save_img=False, hash=True):
        # sample1 area of attack icon:
        smp1_x1 = 0.8708
        smp1_y1 = 0.7556
        smp1_x2 = 0.8979
        smp1_y2 = 0.8009
        
        return self.cal_diff(smp1_x1, smp1_y1, smp1_x2, smp1_y2, self.atk_img, save_img=save_img, hash=hash)
    
        
    def one_turn(self):
        '''
        to run just one-turn battle.
        '''
        NUM = 2
        # Trun number position: (1298, 123), (1335, 164)
        # turn_num_x1 = 0.6760
        # turn_num_y1 = 0.1139
        # turn_num_x2 = 0.6953
        # turn_num_y2 = 0.1519
        
        # next icon:
        
        
        # uodate saved atk icon:
        self.diff_atk = self.cal_atk_diff(targrt=self.atk_img)
        echo_info('INFO', 'save new atk diff:= {}'.format(self.diff_atk))
        
        self.attack()
        time.sleep(3)
        
        # compare atk icon to the last saved icon.
        while 1:
            diff = self.cal_atk_diff(targrt=self.atk_img)
            echo_info('STATUS', 'sampling in the area1, diff=:{}'.format(diff))
            if diff == self.diff_atk:
                n = 0
                for _ in range(NUM):
                    tmp = self.cal_atk_diff(targrt=self.atk_img)
                    time.sleep(0.1)
                    echo_info('INFO', 'last test: now diff=:{}'.format(tmp))
                    if tmp == self.diff_atk:
                        n += 1
                if n==NUM:
                    return 0
            else:
                menu = self.pic_shot_float(self.menu_x1, self.menu_y1, self.menu_x2, self.menu_y2)
                if menu == self.menu_img:
                    echo_info('STATUS', 'Detected status changing, battle finished.')
                    print('------------------------[BATTLE FINISH]--------------------------------')
                    return 1
                
            # click to skip something.
            self.click_act(0.7771, 0.9370, 0)
            time.sleep(SURVEIL_TIME_OUT)
        # res = self.surveil(turn_num_x1, turn_num_y1, turn_num_x2, turn_num_y2, name='[TURN_NUMBER]', save_img=DEBUG)

        
    def one_turn_new(self):   
        # sample1 area of attack icon:(1672, 816), (1724, 865)
        smp1_x1 = 0.8708
        smp1_y1 = 0.7556
        smp1_x2 = 0.8979
        smp1_y2 = 0.8009
        # uodate saved atk icon:
        self.new_atk_img = self.pic_shot_float(smp1_x1, smp1_y1, smp1_x2, smp1_y2)
        echo_info('INFO', 'Save new sample img in area 1.')
        
        self.attack()
        time.sleep(3)
        
        # compare atk icon to the last saved icon.
        while 1:
            now_atk_img = self.pic_shot_float(smp1_x1, smp1_y1, smp1_x2, smp1_y2)
            if now_atk_img == self.new_atk_img:
                echo_info('STATUS', 'Catch status changing in area 1, continue running...')
                return 0
            else:
                echo_info('STATUS', 'No change detected in area 1.')
                now_menu_img = self.pic_shot_float(self.menu_x1, self.menu_y1, self.menu_x2, self.menu_y2)
                
                if DEBUG:
                    diff = compare_img_new(self.menu_img, now_menu_img, algo=1)
                    echo_info('INFO', 'Menu img diff:={}'.format(diff))
                    now_menu_img.save('./data/now_menu.jpg')
                    
                if now_menu_img  == self.menu_img:
                    echo_info('STATUS', 'Detected new status changing, battle finished.')
                    print('------------------------[BATTLE FINISH]----------------------------\n')
                    return 1
                
            # click to skip something
            self.click_act(0.7771, 0.9370, 1)          
            time.sleep(SURVEIL_TIME_OUT)
            
            
    def reuse_skill(self, cd_num):
        skills = []
        for i in range(len(SKILL_CD)):
            if SKILL_CD[i] == cd_num:
                skills.append(i)
        if len(skills):
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
            self.diff_atk = self.wait_loading(save_img=False, sleep=5.5)
            if USE_SKILL:
                self.use_skill(USED_SKILL, timeout=SKILL_SLEEP_TIME)
        
        for i in range(30):
            echo_info('INFO', '--------Start Turn {}--------'.format(i+1))
            
            # Here CD_num == i
            if USE_SKILL:
                self.reuse_skill(i)
            over = self.one_turn_new()
            
            if over:
                return 1
    
    
    def use_apple(self, num):
        flag = 0
        if not USE_APPLE_PER:
            if num in USE_APPLE_ADDITION and num not in DONT_USE_APPLE:
                flag = 1
        else:   
            if (not num % USE_APPLE_PER or num in USE_APPLE_ADDITION) and num not in DONT_USE_APPLE:
                flag = 1
                
        if flag == 1:
            # choose AP bar:
            self.click_act(0.1896, 0.9611, 0.7)
            # choose apple:
            self.click_act(0.5, 0.4463, 0.7)
            # choose OK:
            self.click_act(0.6563, 0.7824, 1)
            
                
    def run(self):
        for j in range(EPOCH):
            print('-----------------------[EPOCH {}]-----------------------------'.format(j))
            self.one_battle() 
            self.use_apple(j+1)
            
            # between battles:
            time.sleep(1)

            


# In[4]:


if __name__ == '__main__':
    fgo = Fgo(full_screen=False, sleep=False)
    #fgo.one_battle(go_on=True)
    fgo.run()


# In[ ]:


# x, y = (1260, 845)
# x/1920, y/1080

