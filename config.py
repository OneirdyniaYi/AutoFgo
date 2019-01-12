# coding: utf-8
# Author: Why
# ======<Mode>======= #
DEBUG = False       # type: bool
CONTINUE_RUN = False    # for debug
# 0 for last position, n for loading from file_n, False for skip:
KEEP_POSITION = False
Choose_item = False  # 万圣节！开始战斗前要选道具
Yili = False        # 剑龙娘三技能：需要满AP使用
# SAVE_IMG = True    # save sll imgs for next runnning.

# ======<Important>======= #
# 0. all
# 1. saber
# 2. archer
# 3. lancer
# 4. rider
# 5. caster
# 6. assassin
# 7. berserker
# 8. special
SUPPORT = 7     # default berserker := 7
EPOCH = 3  # num of battles you want to run (type: int)

CLEAR_AP = False
ONE_APPLE_BATTLE = 3    # all AP // one battle AP cost. (type: int)

# ======<User Setting>======= #
FULL_SCREEN = False  # type: bool

# ultimate skill list: (type: tuple, 1~3), set false to disable.
USED_ULTIMATE = (1, 2, 3)

# use servants' skill or not: (type: bool)
USE_SKILL = True

# skills list: (type: tuple, start from 1)
# reset the order of numbers to change skill orders.
USED_SKILL = (1, 2, 3, 4, 5, 6, 7, 8, 9)
SKILL_MIN_CD = 5

# click to skip something:
CLICK_BREAK_TIME = 1

# # use master's skill or not
# USE_MASTER_SKILL = True
# # The round you want to use in, begin at 0.
# MASTER_SKILL_ROUND = 1
# MASTER_SKILL = (0, 1, 2)
