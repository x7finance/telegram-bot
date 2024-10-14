import random
from datetime import datetime


def RANDOM_BUTTON_TIME():
    time = random.randint(3600, 86400)
    return time

def BURN_AMOUNT():
    amounts = [777, 1000, 1500, 2000]
    time = random.choice(amounts)
    return time


CLICK_ME_ENABLED = True
BURN_ENABLED  = False
BURN_INCREMENT = 25

BUTTON_TIME = None
FIRST_BUTTON_TIME = RANDOM_BUTTON_TIME()
RESTART_TIME = datetime.now().timestamp()

