from disnake.ext import commands, tasks

import os
import aiohttp
import logging
from dotenv import load_dotenv

load_dotenv()


class BotiCord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=60)
    async def post_stats(self):
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": os.environ.get('TOKEN_BOTICORD')}
            json = {"members": len(self.bot.users), "servers": len(self.bot.guilds), "shards": self.bot.shard_count or 1}

            async with session.post("https://api.boticord.top/v3/bots/943215065493041183/stats", headers=headers, json=json) as response:
                if response.status == 201:
                    logging.info("Статистика успешно отправлена (BotiCord)")
                else:
                    logging.info(f"Ошибка: {response.status} (BotiCord)")

    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.user.id == 943215065493041183:
            self.post_stats.start()

def setup(bot):
    bot.add_cog(BotiCord(bot))
