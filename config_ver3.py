# Author: Why
Nero_MAX = False     # 尼禄祭！
DEBUG = False       # type: bool

# ------------------------------[Important]----------------------------------
# num 0~8: [all, saber, archer, lancer, rider, caster, assassin, berserker, special]
SUPPORT = 2     # default berserker := 7 
EPOCH = 50  # num of battles you want to run (type: int)
ONE_APPLE_BATTLE = 3    # all AP // one battle AP cost. (type: int)

# ------------------------------[User Settings]----------------------------------
FULL_SCREEN = False  # type: bool

ATK_BEHIND_FIRST = True

# use ultimate skill or not: (type: bool)
USE_ULTIMATE = False

# use servants' skill or not: (type: bool)
USE_SKILL = False

# skills list:
# type: tuple, num start from 0
USED_SKILL = (0, 1, 2, 3, 4, 5, 6, 7, 8)     # reset the order of numbers to change skill orders.

# time to sleep after using skills, you'd better keep the default value.
# type: float
SKILL_SLEEP_TIME = 2.8

# time to sleep after clicking atk cards:
# you'd better keep the default value.
# type: float
ATK_SLEEP_TIME = 0.1

# click to skip something:
CLICK_BREAK_TIME = 1

# # use master's skill or not 
# USE_MASTER_SKILL = True
# # The round you want to use in, begin at 0.
# MASTER_SKILL_ROUND = 1
# MASTER_SKILL = (0, 1, 2)

#----------------------------[SYNC SETTING]-----------------------------------
# if sending email after code running stop.
# type: bool
SEND_MAIL = True

SEND_MAIL = False if EPOCH<5 or DEBUG else SEND_MAIL
# address and password(not your real password, but a code used for SMTP login service.)
# type: str
FROM_ADDRESS = '344915973@qq.com'
# PASSWD = 'kqddfbmxiipqcaeg'
PASSWD = 'hqytohqljgnebhhg'

# address you want to send mail to.
# type: str
TO_ADDRESS = '694029828@qq.com'

# SMTP server address.
# type: str
SMTP_SERVER = 'smtp.qq.com'

# usable SMTP port, please check at your email settings.
# type: int
SMTP_PORT = 465

# ----------------------------[DON'T EDIT]-----------------------------------
# [WARRNING] dont't edit the following code unless you know what you are doing.

# run config.py to judge that if your screen settings are well-worked.
from PIL import ImageGrab
def test():
    img= ImageGrab.grab()
    img.save('screen_grab_test.jpg')
    

if __name__ == '__main__':
    test()