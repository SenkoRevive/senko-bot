import asyncpg
import os
from datetime import datetime


class SettingsDataBase:
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    async def create_db_pool(cls, bot):
        bot.cursor = await asyncpg.create_pool(os.getenv("TOKEN_DB"))

    async def db_ping(self, bot):
        start_time = datetime.now()
        await bot.cursor.fetch("SELECT now()")
        end_time = datetime.now()
        db_ping = round((end_time - start_time).total_seconds() * 1000)
        return db_ping

    async def delete_data(self, bot, id_server):
        async with bot.cursor.acquire() as conn:
            if await conn.fetchval('SELECT EXISTS(SELECT 1 FROM autorole_settings WHERE id_server = $1)', id_server):
                await conn.execute('DELETE FROM autorole_settings WHERE id_server = $1', id_server)

            if await conn.fetchval('SELECT EXISTS(SELECT 1 FROM logging_settings WHERE id_server = $1)', id_server):
                await conn.execute('DELETE FROM logging_settings WHERE id_server = $1', id_server)

            if await conn.fetchval('SELECT EXISTS(SELECT 1 FROM welcome_settings WHERE id_server = $1)', id_server):
                await conn.execute('DELETE FROM welcome_settings WHERE id_server = $1', id_server)