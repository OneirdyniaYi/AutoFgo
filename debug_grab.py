import autopy
from PIL import Image
import time

input('x1, y1:')
x1, y1 = autopy.mouse.location()
input('x2, y2:')
x2, y2 = autopy.mouse.location()
ori = autopy.bitmap.capture_screen(((x1, y1), (x2-x1, y2-y1)))
ori.save('./ori.png')
while 1:
    now = autopy.bitmap.capture_screen(((x1, y1), (x2-x1, y2-y1)))
    now.save('./now.png')
    print('running...')
    if not (now == ori):
        break
    time.sleep(0.1)
