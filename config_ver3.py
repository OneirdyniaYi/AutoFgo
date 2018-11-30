# coding: utf-8
# Author: Why
# ======<Special Mode>======= #
Nero_MAX = False     # 尼禄祭！误触区域内有高难本
Choose_item = False  # 万圣节！开始战斗前要选道具
Yili = False        # 剑龙娘三技能：需要满AP使用
DEBUG = False       # type: bool

# ======<Important>======= #
# num 0~8: [all, saber, archer, lancer, rider, caster, assassin, berserker, special]
SUPPORT = 7     # default berserker := 7
EPOCH = 6  # num of battles you want to run (type: int)

CLEAR_AP = False
ONE_APPLE_BATTLE = 3    # all AP // one battle AP cost. (type: int)

# ======<User Setting>======= #
FULL_SCREEN = False  # type: bool
ATK_BEHIND_FIRST = False

# ultimate skill list: (type: tuple, 0~2), set false to disable.
USED_ULTIMATE = (0, 1, 2,)
USED_ULTIMATE = (2,)

# use servants' skill or not: (type: bool)
USE_SKILL = True

# skills list: (type: tuple, start from 0)
# reset the order of numbers to change skill orders.
USED_SKILL = (0, 1, 2, 3, 4, 5, 6, 7, 8)
USED_SKILL = (0, 1, 3, 6, 7, 8)

# time to sleep after clicking atk cards:
# you'd better keep the default value.(type: float)
ATK_SLEEP_TIME = 0.1

# click to skip something:
CLICK_BREAK_TIME = 1

# # use master's skill or not
# USE_MASTER_SKILL = True
# # The round you want to use in, begin at 0.
# MASTER_SKILL_ROUND = 1
# MASTER_SKILL = (0, 1, 2)

# ======<Sync Setting>======= #
# if sending email after code running stop.(type: bool)
SEND_MAIL = True
SEND_MAIL = False if EPOCH < 5 or DEBUG else SEND_MAIL
# address and password(not your real password, but a code used for SMTP login service.)
FROM_ADDRESS = '344915973@qq.com'
# PASSWD = 'kqddfbmxiipqcaeg'
PASSWD = 'hqytohqljgnebhhg'

# address you want to send mail to.
TO_ADDRESS = '694029828@qq.com'

# SMTP server address.
SMTP_SERVER = 'smtp.qq.com'

# usable SMTP port, please check at your email settings.(type: int)
SMTP_PORT = 465

# ======<DON'T EDIT>======= #
# dont't edit the following code unless you know what you are doing.
# run config.py to find if your screen settings are well-worked.
from PIL import ImageGrab


def test():
    img = ImageGrab.grab()
    img.save('FullScreenGrab.jpg')


if __name__ == '__main__':
    test()
