import aiomysql
import os


class DBManager:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.port = int(os.getenv("DB_PORT"))
        self.pool = None

    async def _get_pool(self):
        if self.pool is None:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.database,
                port=self.port,
                autocommit=True,
            )
        return self.pool

    async def ping(self):
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    return True
        except Exception as e:
            return f"🔴 MySql: Connection failed: {str(e)}"

    async def _execute_query(
        self,
        query,
        params=None,
        fetch_one=False,
        fetch_all=False,
        commit=False,
    ):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())

                if commit:
                    await conn.commit()

                if fetch_one:
                    return await cur.fetchone()
                if fetch_all:
                    return await cur.fetchall()
                return None

    async def clicks_check_is_fastest(self, time_to_check):
        query = "SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL"
        fastest_time = await self._execute_query(query, fetch_one=True)

        if (
            fastest_time
            and fastest_time[0] is not None
            and isinstance(time_to_check, (int, float))
        ):
            return time_to_check < fastest_time[0]
        return None

    async def clicks_check_highest_streak(self):
        query = """
            SELECT name, streak FROM leaderboard
            WHERE streak = (SELECT MAX(streak) FROM leaderboard WHERE streak > 0)
            LIMIT 1
        """
        return await self._execute_query(query, fetch_one=True)

    async def clicks_fastest_time(self):
        query = """
            SELECT name, MIN(time_taken) FROM leaderboard
            WHERE time_taken = (SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL)
        """
        return await self._execute_query(query, fetch_one=True) or (
            "No user",
            0,
        )

    async def clicks_get_by_name(self, name):
        query = """
            SELECT clicks, time_taken, streak FROM leaderboard WHERE name = %s
        """
        return await self._execute_query(query, (name,), fetch_one=True) or (
            0,
            0,
            0,
        )

    async def clicks_get_leaderboard(self, limit=10):
        query = """
            SELECT name, clicks FROM leaderboard ORDER BY clicks DESC LIMIT %s
        """
        leaderboard_data = await self._execute_query(
            query, (limit,), fetch_all=True
        )

        return (
            "\n".join(
                f"{rank} {name}: {clicks}"
                for rank, (name, clicks) in enumerate(
                    leaderboard_data, start=1
                )
            )
            if leaderboard_data
            else "Error retrieving leaderboard data"
        )

    async def clicks_get_total(self):
        query = "SELECT SUM(clicks) FROM leaderboard"
        result = await self._execute_query(query, fetch_one=True)
        return result[0] if result else 0

    async def clicks_remove(self, name):
        query = """
            UPDATE leaderboard SET clicks = 0, time_taken = NULL, streak = 0 WHERE name = %s
        """
        await self._execute_query(query, (name,), commit=True)
        return "Clicks removed successfully"

    async def clicks_reset(self):
        query = "DELETE FROM leaderboard"
        await self._execute_query(query, commit=True)
        return "Clicks leaderboard reset successfully"

    async def clicks_update(self, name, time_taken):
        user_data = await self.clicks_get_by_name(name)

        if user_data == (0, 0, 0):
            query = "INSERT INTO leaderboard (name, clicks, time_taken, streak) VALUES (%s, 1, %s, 1)"
            params = (name, time_taken)
        else:
            clicks, current_time_taken, current_streak = user_data
            new_time = (
                min(time_taken, current_time_taken)
                if current_time_taken
                else time_taken
            )

            query = """
                UPDATE leaderboard SET clicks = %s, time_taken = %s, streak = %s WHERE name = %s
            """
            params = (clicks + 1, new_time, current_streak + 1, name)

        await self._execute_query(query, params, commit=True)

        await self._execute_query(
            "UPDATE leaderboard SET streak = 0 WHERE name <> %s",
            (name,),
            commit=True,
        )

        return f"User {name}'s click record updated successfully."

    async def count_launches(self):
        query = "SELECT amount FROM log WHERE name = 'deployed'"
        result = await self._execute_query(query, fetch_one=True)
        return result[0] if result else 0

    async def settings_set(self, setting_name, value):
        query = "UPDATE settings SET value = %s WHERE setting_name = %s"
        await self._execute_query(
            query, (1 if value else 0, setting_name), commit=True
        )

    async def settings_get(self, setting_name):
        query = "SELECT value FROM settings WHERE setting_name = %s"
        result = await self._execute_query(
            query, (setting_name,), fetch_one=True
        )
        return result[0] == 1 if result else False

    async def settings_get_all(self):
        query = "SELECT setting_name, value FROM settings"
        results = await self._execute_query(query, fetch_all=True)
        return (
            {setting: value == 1 for setting, value in results}
            if results
            else {}
        )

    async def wallet_add(self, user_id, wallet, private_key):
        query = "SELECT 1 FROM wallets WHERE user_id = %s"
        user_exists = await self._execute_query(
            query, (user_id,), fetch_one=True
        )

        if user_exists:
            return "Error: You already have a wallet registered, use /me in private to view it"

        query = "INSERT INTO wallets (user_id, wallet, private_key) VALUES (%s, %s, %s)"
        await self._execute_query(
            query, (user_id, wallet, private_key), commit=True
        )

        return "Wallet added successfully"

    async def wallet_count(self):
        query = "SELECT COUNT(DISTINCT user_id) FROM wallets"
        result = await self._execute_query(query, fetch_one=True)
        return result[0] if result else "N/A"

    async def wallet_get(self, user_id):
        if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
            return {
                "user_id": user_id,
                "wallet": os.getenv("BURN_WALLET"),
                "private_key": os.getenv("BURN_WALLET_PRIVATE_KEY"),
            }

        query = "SELECT wallet, private_key FROM wallets WHERE user_id = %s"
        result = await self._execute_query(query, (user_id,), fetch_one=True)

        return (
            {"user_id": user_id, "wallet": result[0], "private_key": result[1]}
            if result
            else None
        )

    async def wallet_remove(self, user_id):
        query = "DELETE FROM wallets WHERE user_id = %s"
        affected_rows = await self._execute_query(
            query, (user_id,), commit=True
        )

        if affected_rows:
            return f"Wallet entry for user ID {user_id} removed."
        return f"No wallet entry found for user ID {user_id}."
