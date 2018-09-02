
# coding: utf-8

# In[2]:


import PIL
from PIL import ImageGrab
import time 
import numpy as np


# In[5]:


def pic_shot(x1, y1, x2, y2, fname=None):
    beg = time.time()
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    # img = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
    if fname:
        img.save(fname)
    end = time.time()
    # print('[SHOT {}] Get pic: {}, Time Use: {} s'.format(time.strftime('%H:%M:%S'), fname, end - beg))
    return img


# In[4]:


def echo_info(name, info):
    print('[{} {}] '.format(name, time.strftime('%H:%M:%S')) + info)


# In[7]:


def getColor(img, x, y):
    # h(y)*w(x)*3
    img = np.array(img)
    pix = img[y][x]
    # img[y][x] = (230, 0, 0)
    # pix = PIL.Image.fromarray(img)
    return pix


# In[28]:


RESIZE_W = 9
RESIZE_H = 8

def get_hash(img):
    small_img = img.resize((RESIZE_W, RESIZE_H))
    small_img.save('tmp1.jpg')
    gray_img = small_img.convert("L")
    gray_img.save('tmp2.jpg')
    pixels = list(gray_img.getdata())
    diff = []
    for row in range(RESIZE_H):    
        row_start_index = row * RESIZE_W    
        for col in range(RESIZE_W - 1):        
            left_pixel_index = row_start_index + col
            diff.append(pixels[left_pixel_index] > pixels[left_pixel_index + 1])

    decimal_value = 0
    hash_string = ""
    for index, value in enumerate(diff):    
        if value:       
            decimal_value += value * (2 ** (index % 8))   
        if index % 8 == 7:      
            hash_string += str(hex(decimal_value)[2:].rjust(2, "0"))       
            decimal_value = 0
    return hash_string


def compare_img(img1, img2):
    dhash1 = get_hash(img1)
    dhash2 = get_hash(img2)

    # calculate hamming distance:
    diff = (int(dhash1, 16)) ^ (int(dhash2, 16))
    return bin(diff).count("1")

    


# In[31]:


# img = pic_shot(0, 0, 400, 200)
# compare_img(img, img2)
# getColor(img, 10, 45)

