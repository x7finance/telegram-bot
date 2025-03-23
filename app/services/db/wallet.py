import json
import os
from . import DBManager


class WalletManager(DBManager):
    async def add(self, user_id, wallet, private_key):
        query = "SELECT 1 FROM wallets WHERE user_id = %s"
        user_exists = await self._execute_query(
            query, (user_id,), fetch_one=True
        )

        if user_exists:
            return "Error: You already have a wallet registered, use /me in private to view it"

        empty_reminders = json.dumps([])

        query = "INSERT INTO wallets (user_id, wallet, private_key, reminders) VALUES (%s, %s, %s, %s)"
        await self._execute_query(
            query, (user_id, wallet, private_key, empty_reminders), commit=True
        )

        return "Wallet added successfully"

    async def count(self):
        query = "SELECT COUNT(DISTINCT user_id) FROM wallets"
        result = await self._execute_query(query, fetch_one=True)
        return result[0] if result else "N/A"

    async def get(self, user_id):
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

    async def remove(self, user_id):
        query = "DELETE FROM wallets WHERE user_id = %s"
        affected_rows = await self._execute_query(
            query, (user_id,), commit=True
        )

        if affected_rows:
            return f"Wallet entry for user ID {user_id} removed."
        return f"No wallet entry found for user ID {user_id}."
