# debug mode:
# type: bool
DEBUG = True

# set full screen mode to get better effect.
# type: bool
FULL_SCREEN = False

# num of battles you want to run:
# type: int
EPOCH = 4

# num 0~8, options: [all, saber, archer, lancer, rider, caster, assassin, berserker, special]
# type: int
SUPPORT = 7     # default berserker


# ----------------------------[BATTLE SETTING]---------------------------------
# use ultimate skill or not:
# type: bool
USE_ULTIMATE = False

# use servants' skill or not:
# [WARNING]: skills can't select the target, Take effect immediately.
# type: bool
USE_SKILL = False

# set small number to avoid bugs of skill using caused by servants' death.
# set 0 to skip using skills.
# type: int 
# USE_SKILL_TIMES = 2

# CD turns of each skill of YOUR SERVANTS.(set all skills, although you won't use all of them):
# the Nth num is the Nth skill's CD time, without support servant.
# type: int
YOUR_SKILL_CD = (7, 8, 7, 6, 8, 9)

# set a big number to ensure that skills won't be used wrongly.
# type: int
SUPPORT_SKILL_CD = 8

# skills list:
# type: tuple, num start from 0
USED_SKILL = (0, 1, 2, 3, 4, 5, 6, 7, 8)     # reset the order of numbers to change skill orders.

# time to sleep after using skills:
# you'd better keep the default value.
# type: float
SKILL_SLEEP_TIME = 2.5


# # use master's skill or not 
# USE_MASTER_SKILL = True
# # The round you want to use in, begin at 0.
# MASTER_SKILL_ROUND = 1
# MASTER_SKILL = (0, 1, 2)

# Surveillance timeout in sample 1(atk icon):
# type: float
SURVEIL_TIME_OUT = 0.5


# ----------------------------[APPLE USING]---------------------------------
# use apple per n battles. default use the golden apple. Please calculate by yourself. set 'False' to skip using. 
# type: int
USE_APPLE_PER = False

# additions of apple using, set numbers for epoch No. Use apple AFTER that epoch.
# type: tuple, num start from 1
USE_APPLE_ADDITION = ()

# details of don't using apple, if there are conflicts, it will cover `USE_APPLE_DETAIL` and 'APPLE_USE'.
# type: tuple, num start from 1
DONT_USE_APPLE = ( )

# ----------------------------[DON'T EDIT]-----------------------------------
# [WARRNING] dont't edit the following code.

# run config.py to judge that if your screen settings are well-worked.
from PIL import ImageGrab
def test():
    img= ImageGrab.grab()
    img.save('screen_grab_test.jpg')
    

if __name__ == '__main__':
    test()