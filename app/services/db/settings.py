from . import DBManager


class SettingsManager(DBManager):
    async def set(self, setting_name, value):
        query = "UPDATE settings SET value = %s WHERE setting_name = %s"
        await self._execute_query(
            query, (1 if value else 0, setting_name), commit=True
        )

    async def get(self, setting_name):
        query = "SELECT value FROM settings WHERE setting_name = %s"
        result = await self._execute_query(
            query, (setting_name,), fetch_one=True
        )
        return result[0] == 1 if result else False

    async def get_all(self):
        query = "SELECT setting_name, value FROM settings"
        results = await self._execute_query(query, fetch_all=True)
        return (
            {setting: value == 1 for setting, value in results}
            if results
            else {}
        )
