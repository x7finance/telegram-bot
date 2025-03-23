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

    async def ping(self):
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    return True
        except Exception as e:
            return f"🔴 MySql: Connection failed: {str(e)}"
