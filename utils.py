
# coding: utf-8

# In[6]:


import PIL
from PIL import ImageGrab
import time 
import ctypes


# In[1]:


def pic_shot(x1, y1, x2, y2, fname):
    beg = time.time()
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    # img = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
    img.save(fname)
    end = time.time()
    print('[Screen Shot] Get pic: {}, Time Use: {} s'.format(fname, end - beg))
    return img


# In[ ]:


def window_capture_win32(filename):
      hwnd = 0     # num of window.
      hwndDC = win32gui.GetWindowDC(hwnd)
      mfcDC = win32ui.CreateDCFromHandle(hwndDC)
      saveDC = mfcDC.CreateCompatibleDC()
      saveBitMap = win32ui.CreateBitmap()
      # get monitor info.
      # MoniterDev = win32api.EnumDisplayMonitors(None, None)
      # w = MoniterDev[0][2][2]
      # h = MoniterDev[0][2][3]
      w = 500
      h = 200
      # create new space for bitmap.
      saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
      saveDC.SelectObject(saveBitMap)
      # shot a (h, w) pic.
      saveDC.BitBlt((100, 100), (w, h), mfcDC, (0, 100), win32con.SRCCOPY)
      saveBitMap.SaveBitmapFile(saveDC, filename)


# In[9]:


STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE= -11
STD_ERROR_HANDLE = -12
 
FOREGROUND_BLACK = 0x0
FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED = 0x04 # text color contains red.
FOREGROUND_INTENSITY = 0x08 # text color is intensified.
 
BACKGROUND_BLUE = 0x10 # background color contains blue.
BACKGROUND_GREEN= 0x20 # background color contains green.
BACKGROUND_RED = 0x40 # background color contains red.
BACKGROUND_INTENSITY = 0x80 # background color is intensified.
 
class Color:
    ''' See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
    for information on Windows APIs.'''
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    
    def set_cmd_color(self, color, handle=std_out_handle):
        """(color) -> bit
        Example: set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        """
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool
    
    def reset_color(self):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)
    
    def print_red(self, print_text):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
        print(print_text)
        self.reset_color()
        
    def print_green(self, print_text):
        self.set_cmd_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        print(print_text)

