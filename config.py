# Author: Why
Nero_MAX = True     # 尼禄祭！
DEBUG = False       # type: bool
# Advanced work:
# - Skip the confirming of using skills.
# - set battle speed to 2x
# - make sure your team formation has been finished.
# - set the proper order of support servants.
# - edit the following settings each time you run main.py.


# ------------------------------[User Settings]----------------------------------
FULL_SCREEN = False  # type: bool
 
# num 0~8, options: [all, saber, archer, lancer, rider, caster, assassin, berserker, special]
# type: int
SUPPORT = 7     # default berserker := 7 

EPOCH = 40  # num of battles you want to run (type: int)
# ----------------------------[APPLE USING]---------------------------------
# equal ot all AP // one battle AP cost.
# type: int
ONE_APPLE_BATTLE = 3

# INIT_AP = 179  # AP before running code.(type: int)

# # AP one battle costed.
# # type: int
# BATTLE_AP_COST = 40

# # AP of one apple. default golden apple(137)
# # type: int
# ONE_APPLE_AP = 136

# # use up all AP or not. Auto change epoch.
# # type: bool
# CLEAR_AP = True
# ----------------------------[BATTLE SETTING]---------------------------------
# attack enemy behind firstly. `USE_ULTIMATE` may disturb this API.
# type: bool
ATK_BEHIND_FIRST = True

# use ultimate skill or not:
# type: bool
USE_ULTIMATE = True

# use servants' skill or not:
# [WARNING]: skills can't select the target, Take effect immediately.
# type: bool
USE_SKILL = True

# set small number to avoid bugs of skill using caused by servants' death.
# set 0 to skip using skills.
# type: int 
# USE_SKILL_TIMES = 2

# CD turns of each skill of YOUR SERVANTS.(set all skills, although you won't use all of them):
# the Nth num is the Nth skill's CD time, without support servant.
# type: int
# YOUR_SKILL_CD = (8, 6, 8, 5, 7, 8)    # 酒吞
# YOUR_SKILL_CD = (7, 7, 12, 5, 7, 8)  # 恩奇都
YOUR_SKILL_CD = (7, 6, 7, 5, 7, 8)    # 金时


# set a big number to ensure that skills won't be used wrongly.
# type: int
SUPPORT_SKILL_CD = 6

# skills list:
# type: tuple, num start from 0
USED_SKILL = (0, 1, 2, 3, 4, 5, 6, 7, 8)     # reset the order of numbers to change skill orders.

# time to sleep after using skills:
# you'd better keep the default value.
# type: float
SKILL_SLEEP_TIME = 2.8

# time to sleep after clicking atk cards:
# you'd better keep the default value.
# type: float
ATK_SLEEP_TIME = 0.1

# # use master's skill or not 
# USE_MASTER_SKILL = True
# # The round you want to use in, begin at 0.
# MASTER_SKILL_ROUND = 1
# MASTER_SKILL = (0, 1, 2)

# Surveillance timeout in sample 1(atk icon):
# type: float
# SURVEIL_TIME_OUT = 0.5

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