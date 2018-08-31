
# coding: utf-8

# In[33]:


import win32api, win32con, win32gui, win32ui
from PIL import ImageGrab
import time
from config import *
from utils import Color, pic_shot


# In[34]:


def pic_shot(x1, y1, x2, y2, fname):
    beg = time.time()
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    # img = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
    img.save(fname)
    end = time.time()
    print('[Screen Shot] Get pic: {}, Time Use: {} s'.format(fname, end - beg))
    return img


# In[35]:


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


# In[38]:


class Fgo(object):
    def __init__(self, full_screen=True, supNo=8):
        # [init by yourself] put cursor at the down-right position of the game window.
        self.coloer = Color()
        if full_screen:
            self.height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            self.width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            self.scr_pos1 = (0, 0)
            self.scr_pos2 = (self.width, self.height)
            self.c = Cursor(init_pos=False)
        
        else:
            self.c = Cursor(init_pos=False)
            while 1:
                input('[INFO {}] Move cursor to the top-left cornor of Fgo screen, and press ENTER:'.format(time.strftime('%H:%M:%S')))
                self.scr_pos1 = self.c.get_pos()
                print('[INFO {}] Get cursor at {}'.format(time.strftime('%H:%M:%S'), self.scr_pos1))
                
                input('[INFO {}] Move cursor to the down-right cornor of Fgo screen, and press ENTER:'.format(time.strftime('%H:%M:%S')))
                self.scr_pos2 = self.c.get_pos()
                print('[INFO {}] Get cursor at {}'.format(time.strftime('%H:%M:%S'), self.scr_pos2))
                
                res = input('[INFO {}] Continue?[y/n](y to continue, n to reset cursor):'.format(time.strftime('%H:%M:%S')))
                if res == 'y':
                    break
            
            self.width = abs(self.scr_pos2[0] - self.scr_pos1[0])
            self.height = abs(self.scr_pos2[1] - self.scr_pos1[1])
            
        
        #---------------------position info-----------------------
        # postion of the center of battle tag.
        self.bat_tag_y = 0.2740
        self.bat_tag_x = 0.7252
        # postion of support servant tag.
        self.sup_tag_x = 0.4893
        self.sup_tag_y = 0.3944
        # postion of support class icon.
        self.sup_ico_x = 0.0729+0.0527*supNo
        self.sup_ico_y = 0.1796
        # postion of `mission start` tag
        self.start_x = 0.9281
        self.start_y = 0.9398
        
        print('\n---------------------[init over]---------------------------')
        print('[DEBUG {}] Window width(x) = {}, height(y) = {}'.format(time.strftime('%H:%M:%S'), self.width, self.height))
        
    
    def _set(self, float_x, float_y):
        # input type: float
        return int(self.scr_pos1[0]+self.width*float_x), int(self.scr_pos1[1]+self.height*float_y)
    
    def click_act(self, float_x, float_y, sleep_time, click=True):
        pos = self._set(float_x, float_y)
        self.c.move_to(pos)
        if click:
            self.c.click()
        print('[INFO {}] simulate click at position: {}'.format(time.strftime('%H:%M:%S'), pos))
        time.sleep(sleep_time)
    
    def enter_battle(self):
        # [init by yourself] put the tag of battle at the top of screen.
        self.click_act(self.bat_tag_x, self.bat_tag_y, 1.5)
        
        # choose support:
        self.click_act(self.sup_ico_x, self.sup_ico_y, 1)
        self.click_act(self.sup_tag_x, self.sup_tag_y, 2)
        
        # game start
        self.click_act(self.start_x, self.start_y, 3, click=True)
        


# In[39]:


fgo = Fgo(full_screen=FULL_SCREEN, supNo=SUPPORT)
fgo.enter_battle()


# In[32]:


'''w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
print(w, h)
c = Cursor(init_pos=False)
c.get_pos()
# c = Cursor(init_pos=False)
# c.right_click()
#c.move_to((w, h))'''

