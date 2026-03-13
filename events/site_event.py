from disnake.ext import commands, tasks

import os
import aiohttp
import logging
from dotenv import load_dotenv

load_dotenv()


class Site(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=60)
    async def post_stats(self):
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": os.environ.get('TOKEN_API')}
            json = {"servers": len(self.bot.guilds), "user": len(self.bot.users)}

            async with session.post("https://senko-bot.com/send-data", headers=headers, json=json) as response:
                if response.status == 201:
                    logging.info("Статистика успешно отправлена (Site)")
                else:
                    logging.info(f"Ошибка: {response.status} (Site)")

    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.user.id == 943215065493041183:
            self.post_stats.start()

def setup(bot):
    bot.add_cog(Site(bot))
