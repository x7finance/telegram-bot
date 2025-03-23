from . import DBManager


class ClicksManager(DBManager):
    async def get_highest_streak(self):
        query = """
            SELECT name, streak FROM leaderboard
            WHERE streak = (SELECT MAX(streak) FROM leaderboard WHERE streak > 0)
            LIMIT 1
        """
        return await self._execute_query(query, fetch_one=True)

    async def get_fastest_time(self):
        query = """
            SELECT name, MIN(time_taken) FROM leaderboard
            WHERE time_taken = (SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL)
        """
        return await self._execute_query(query, fetch_one=True) or (
            "No user",
            0,
        )

    async def get(self, name):
        query = """
            SELECT clicks, time_taken, streak FROM leaderboard WHERE name = %s
        """
        return await self._execute_query(query, (name,), fetch_one=True) or (
            0,
            0,
            0,
        )

    async def get_leaderboard(self, limit=10):
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

    async def get_total(self):
        query = "SELECT SUM(clicks) FROM leaderboard"
        result = await self._execute_query(query, fetch_one=True)
        return result[0] if result else 0

    async def remove(self, name):
        query = """
            UPDATE leaderboard SET clicks = 0, time_taken = NULL, streak = 0 WHERE name = %s
        """
        await self._execute_query(query, (name,), commit=True)
        return "Clicks removed successfully"

    async def reset(self):
        query = "DELETE FROM leaderboard"
        await self._execute_query(query, commit=True)
        return "Clicks leaderboard reset successfully"

    async def update(self, name, time_taken):
        user_data = await self.get(name)

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

    async def is_fastest(self, time_to_check):
        query = "SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL"
        fastest_time = await self._execute_query(query, fetch_one=True)

        if (
            fastest_time
            and fastest_time[0] is not None
            and isinstance(time_to_check, (int, float))
        ):
            return time_to_check < fastest_time[0]
        return None
