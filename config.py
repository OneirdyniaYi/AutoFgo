# debug mode:
DEBUG = True

# set full screen mode to get better effect.
FULL_SCREEN = False

# num of battles you want to run:
EPOCH = 20

# num 0~8, options: [all, saber, archer, lancer, rider, caster, assassin, berserker, special]
SUPPORT = 7     # default berserker

# use ultimate skill or not:
USE_ULTIMATE = True

# use servants' skill or not:
# [WARNING]: skills can't select the target, Take effect immediately.
USE_SKILL = True
USED_SKILL = (0, 1, 2, 3, 4, 5, 6, 7, 8)     # reset the order of numbers to change skill orders.
USED_SKILL = (0, 1, 2, 3, 5, 6, 8)
SKILL_SLEEP_TIME = 3      # time to sleep after using skills.


# # use master's skill or not 
# USE_MASTER_SKILL = True
# # The round you want to use in, begin at 0.
# MASTER_SKILL_ROUND = 1
# MASTER_SKILL = (0, 1, 2)

# Surveillance timeout in sample 1(atk icon):
SURVEIL_TIME_OUT = 0.5

# get megic cubes or stones after the first battle.
GET_CUBES_FIRST_TIME = True

# times to sleep after a battle ending.(to find that if sample area has changed)
BATTLE_END_TIMEOUT = 8


# -----------------------------------------------------------------------------
# [WARRNING] dont't edit the following code.

# run config.py to judge that if your screen settings are well-worked.
from PIL import ImageGrab
def test():
    img= ImageGrab.grab()
    img.save('screen_grab_test.jpg')
    

if __name__ == '__main__':
    test()