from .base import DBManager
from .clicks import ClicksManager
from .launcher import LauncherManager
from .reminders import RemindersManager
from .settings import SettingsManager
from .wallet import WalletManager


class DBNamespace:
    def __init__(self):
        self._base = DBManager()
        self.clicks = ClicksManager()
        self.launcher = LauncherManager()
        self.reminders = RemindersManager()
        self.settings = SettingsManager()
        self.wallet = WalletManager()

    async def ping(self):
        return await self._base.ping()


db = DBNamespace()
