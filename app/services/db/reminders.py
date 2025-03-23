import json
from . import DBManager


class RemindersManager(DBManager):
    async def add(self, user_id, when, message):
        current = await self.get(user_id)

        new_reminder = {
            "time": when.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
        }

        if current:
            reminders = current["reminders"]
            reminders.append(new_reminder)
        else:
            reminders = [new_reminder]

        query = """
            UPDATE wallets 
            SET reminders = %s
            WHERE user_id = %s
        """
        await self._execute_query(
            query, (json.dumps(reminders), user_id), commit=True
        )

    async def get(self, user_id):
        query = "SELECT reminders FROM wallets WHERE user_id = %s"
        result = await self._execute_query(query, (user_id,), fetch_one=True)

        if not result or not result[0]:
            return False

        return {"user_id": user_id, "reminders": json.loads(result[0])}

    async def remove(self, user_id, when=None):
        if when:
            current = await self.get(user_id)
            if current:
                reminders = current["reminders"]
                reminders = [
                    r
                    for r in reminders
                    if r["time"] != when.strftime("%Y-%m-%d %H:%M:%S")
                ]

                query = """
                    UPDATE wallets 
                    SET reminders = %s
                    WHERE user_id = %s
                """
                await self._execute_query(
                    query, (json.dumps(reminders), user_id), commit=True
                )
        else:
            query = """
                UPDATE wallets 
                SET reminders = NULL
                WHERE user_id = %s
            """
            await self._execute_query(query, (user_id,), commit=True)

    async def get_all(self):
        query = """
            SELECT user_id, reminders 
            FROM wallets 
            WHERE reminders IS NOT NULL
        """
        results = await self._execute_query(query, fetch_all=True)

        if not results:
            return []

        all_reminders = []
        for user_id, reminders_json in results:
            reminders = json.loads(reminders_json)
            for reminder in reminders:
                all_reminders.append(
                    {
                        "user_id": user_id,
                        "reminder_time": reminder["time"],
                        "reminder_message": reminder["message"],
                    }
                )

        return all_reminders
