import os
import mafic
import logging
import asyncio
import traceback

import disnake
from events.bot_event import BotEvents
from disnake.ext import commands, tasks


class YoutubeUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=60)
    async def check_account(self):
        guild = self.bot.get_guild(1064586888989642843)
        channel = self.bot.get_channel(1064586891351040013)
        player = mafic.Player(guild, channel)

        await asyncio.sleep(600)

        try:
            tracks = await player.fetch_tracks("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            if not tracks:
                logging.info("YouTube недоступен (ролик не найден)")
                await BotEvents.error_log(content="<@&963680868147265556> YouTube недоступен (ролик не найден)", file=disnake.File("./data/gluhka.webp"), self=None)
            else:
                logging.info("YouTube доступен")
        except Exception as error:
            logging.info("YouTube недоступен (неизвестная ошибка)")

            f = open(f'./data/error_traceback_youtube.txt', 'w')
            f.write(str(''.join(traceback.format_exception(type(error), error, error.__traceback__))))
            f.close()

            await BotEvents.error_log(content="<@&963680868147265556> YouTube недоступен (ролик не найден)", file=disnake.File("./data/error_traceback_youtube.txt"), self=None)

            os.remove(f"./data/error_traceback_youtube.txt")

    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.user.id == 943215065493041183:
            self.check_account.start()


def setup(bot):
    bot.add_cog(YoutubeUpdater(bot))
