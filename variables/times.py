# TIMES

import random
from datetime import datetime


# AUTO TIMES SECONDS
def RANDOM_BUTTON_TIME():
    time = random.randint(3600, 86400)
    return time

FIRST_BUTTON_TIME = RANDOM_BUTTON_TIME()
RESTART_TIME = datetime.now().timestamp()
BUTTON_TIME = None

# COUNTDOWN
COUNTDOWN_TIME = datetime(2023, 9, 7, 12, 00, 00)
COUNTDOWN_TITLE = "Xchange launch"
COUNTDOWN_TITLE = "https://app.x7.finance"

# LAUNCH DATES
X7M105 = datetime(2022, 8, 13, 13, 10, 17)
MIGRATION = datetime(2022, 9, 25, 4, 0, 11)

# BURN
def BURN_AMOUNT():
    amounts = [777, 1000, 1500, 2000]
    time = random.choice(amounts)
    return time

BURN_INCREMENT = 5
