import random
from datetime import datetime

from constants.protocol import addresses


def random_button_time():
    time = random.randint(3600, 86400)
    return time


def burn_amount():
    amounts = [777, 1000, 1500, 2000]
    time = random.choice(amounts)
    return time


BURN_TOKEN = addresses.x7r("eth")
BUTTON_TIME = None
CLICK_ME_BURN = 50
FIRST_BUTTON_TIME = random_button_time()
RESTART_TIME = datetime.now().timestamp()
