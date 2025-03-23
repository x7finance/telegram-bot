from . import DBManager


class LauncherManager(DBManager):
    async def count(self):
        query = "SELECT amount FROM log WHERE name = 'deployed'"
        result = await self._execute_query(query, fetch_one=True)
        return result[0] if result else 0
