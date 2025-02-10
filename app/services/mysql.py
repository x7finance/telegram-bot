import mysql.connector
import os


class MySql:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.port = os.getenv("DB_PORT")

    def _connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
        )

    def _execute_query(
        self,
        query,
        params=None,
        fetch_one=False,
        fetch_all=False,
        commit=False,
    ):
        connection = None
        cursor = None
        try:
            connection = self._connect()
            cursor = connection.cursor()
            cursor.execute(query, params or ())

            if commit:
                connection.commit()

            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()

        except mysql.connector.Error:
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def clicks_check_is_fastest(self, time_to_check):
        query = "SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL"
        fastest_time = self._execute_query(query, fetch_one=True)

        if (
            fastest_time
            and fastest_time[0] is not None
            and isinstance(time_to_check, (int, float))
        ):
            return time_to_check < fastest_time[0]
        return None

    def clicks_check_highest_streak(self):
        query = """
            SELECT name, streak FROM leaderboard
            WHERE streak = (SELECT MAX(streak) FROM leaderboard WHERE streak > 0)
            LIMIT 1
        """
        return self._execute_query(query, fetch_one=True)

    def clicks_fastest_time(self):
        query = """
            SELECT name, MIN(time_taken) FROM leaderboard
            WHERE time_taken = (SELECT MIN(time_taken) FROM leaderboard WHERE time_taken IS NOT NULL)
        """
        return self._execute_query(query, fetch_one=True) or ("No user", 0)

    def clicks_get_by_name(self, name):
        query = """
            SELECT clicks, time_taken, streak FROM leaderboard WHERE name = %s
        """
        return self._execute_query(query, (name,), fetch_one=True) or (0, 0, 0)

    def clicks_get_leaderboard(self, limit=10):
        query = """
            SELECT name, clicks FROM leaderboard ORDER BY clicks DESC LIMIT %s
        """
        leaderboard_data = self._execute_query(query, (limit,), fetch_all=True)

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

    def clicks_get_total(self):
        query = "SELECT SUM(clicks) FROM leaderboard"
        result = self._execute_query(query, fetch_one=True)
        return result[0] if result else 0

    def clicks_remove(self, name):
        query = """
            UPDATE leaderboard SET clicks = 0, time_taken = NULL, streak = 0 WHERE name = %s
        """
        self._execute_query(query, (name,), commit=True)
        return "Clicks removed successfully"

    def clicks_reset(self):
        query = "DELETE FROM leaderboard"
        self._execute_query(query, commit=True)
        return "Clicks leaderboard reset successfully"

    def clicks_update(self, name, time_taken):
        user_data = self.clicks_get_by_name(name)

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

        self._execute_query(query, params, commit=True)

        self._execute_query(
            "UPDATE leaderboard SET streak = 0 WHERE name <> %s",
            (name,),
            commit=True,
        )

        return f"User {name}'s click record updated successfully."

    def settings_set(self, setting_name, value):
        query = "UPDATE settings SET value = %s WHERE setting_name = %s"
        self._execute_query(
            query, (1 if value else 0, setting_name), commit=True
        )

    def settings_get(self, setting_name):
        query = "SELECT value FROM settings WHERE setting_name = %s"
        result = self._execute_query(query, (setting_name,), fetch_one=True)
        return result[0] == 1 if result else False

    def settings_get_all(self):
        query = "SELECT setting_name, value FROM settings"
        results = self._execute_query(query, fetch_all=True)
        return (
            {setting: value == 1 for setting, value in results}
            if results
            else {}
        )

    def wallet_add(self, user_id, wallet, private_key):
        query = "SELECT 1 FROM wallets WHERE user_id = %s"
        user_exists = self._execute_query(query, (user_id,), fetch_one=True)

        if user_exists:
            return "Error: You already have a wallet registered, use /me in private to view it"

        query = "INSERT INTO wallets (user_id, wallet, private_key) VALUES (%s, %s, %s)"
        self._execute_query(query, (user_id, wallet, private_key), commit=True)

        return "Wallet added successfully"

    def wallet_count(self):
        query = "SELECT COUNT(DISTINCT user_id) FROM wallets"
        result = self._execute_query(query, fetch_one=True)
        return result[0] if result else "N/A"

    def wallet_get(self, user_id):
        if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
            return {
                "user_id": user_id,
                "wallet": os.getenv("BURN_WALLET"),
                "private_key": os.getenv("BURN_WALLET_PRIVATE_KEY"),
            }

        query = "SELECT wallet, private_key FROM wallets WHERE user_id = %s"
        result = self._execute_query(query, (user_id,), fetch_one=True)

        return (
            {"user_id": user_id, "wallet": result[0], "private_key": result[1]}
            if result
            else None
        )

    def wallet_remove(self, user_id):
        query = "DELETE FROM wallets WHERE user_id = %s"
        affected_rows = self._execute_query(query, (user_id,), commit=True)

        if affected_rows:
            return f"Wallet entry for user ID {user_id} removed."
        return f"No wallet entry found for user ID {user_id}."
