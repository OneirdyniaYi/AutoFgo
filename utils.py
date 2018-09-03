
# coding: utf-8

# In[2]:


import PIL
from PIL import ImageGrab
import time 
import numpy as np
import cv2


# In[3]:


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


# In[5]:


def getColor(img, x, y):
    # h(y)*w(x)*3
    img = np.array(img)
    pix = img[y][x]
    # img[y][x] = (230, 0, 0)
    # pix = PIL.Image.fromarray(img)
    return pix


# In[6]:


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



# In[7]:


def get_global_color(img):
    img = np.array(img)
    color = [a[:, :, x].mean() for x in range(3)]
    return np.array(color)

def compare_RGB(img1, img2):
    c1 = get_global_color(img1)
    c2 = get_global_color(img2)
    return np.sqrt(np.sum([(c1[i]-c2[i])**2 for i in range(3)]))


# In[8]:


def aHash(img):
    img = np.array(img)
    img=cv2.resize(img,(8,8),interpolation=cv2.INTER_CUBIC)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    s=0
    hash_str=''
    for i in range(8):
        for j in range(8):
            s=s+gray[i,j]
    avg=s/64
    for i in range(8):
        for j in range(8):
            if  gray[i,j]>avg:
                hash_str=hash_str+'1'
            else:
                hash_str=hash_str+'0'            
    return hash_str

def dHash(img):
    img = np.array(img)
    img=cv2.resize(img,(9,8),interpolation=cv2.INTER_CUBIC)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    hash_str=''
    for i in range(8):
        for j in range(8):
            if   gray[i,j]>gray[i,j+1]:
                hash_str=hash_str+'1'
            else:
                hash_str=hash_str+'0'
    return hash_str

def cmpHash(hash1,hash2):
    n=0
    if len(hash1)!=len(hash2):
        return -1
    for i in range(len(hash1)):
        if hash1[i]!=hash2[i]:
            n=n+1
    return n

def compare_img_new(img1, img2, algo):
    hash = aHash if algo==0 else dHash
    h1 = hash(img1)
    h2 = hash(img2)
    return cmpHash(h1, h2)

