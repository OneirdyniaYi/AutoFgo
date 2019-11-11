import cv2
import numpy as np
from PIL import Image


def cal_single_hist(image1, image2):
    # calculate gray hist similarity for a single channel.
    # image1, image2: [h, w, 3] shape numpy.ndarray
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    degree = 0
    for h1, h2 in zip(hist1, hist2):
        degree += (1 - abs(h1 - h2) / max(h1, h2)) if h1 != h2 else 1
    return degree / len(hist1)


def similar(img1, img2, bound=0.5, name=False, size=(128, 128)):
    # to find if 2 imgs ([h, w, 3] numpy.ndarray) are similar.
    # calculate hist similarity for 3 channels.
    # - bound: if 2 imgs' similarity in RGB > bounds, return True.

    image1 = np.array(img1)
    image2 = np.array(img2)
    sub_image1 = cv2.split(cv2.resize(image1, size))
    sub_image2 = cv2.split(cv2.resize(image2, size))
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += cal_single_hist(im1, im2)

    res = (sub_data / 3)[0] if type(sub_data) != float else sub_data / 3

    if name and res > 0.5:
        print(f'+ Name: [{name}] Similarity: {res:.4f}, bound: {bound}')
    # d +0.0001 to avoid that d == 0
    return res if res > bound else False


def bmp2pil(im):
    # convert bitmap image to PIL format.
    width, height = int(round(im.width * im.scale)
                        ), int(round(im.height * im.scale))
    return Image.frombytes('RGB', (width, height), bytes(im))
