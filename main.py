import os
import logging
import importlib
from datetime import datetime

from dotenv import load_dotenv

import disnake
from disnake.ext import commands

from settings.settings_music import Setup
from settings.command_model import Comamnd
from settings.settings_db import SettingsDataBase

load_dotenv()
bot = Setup(intents=disnake.Intents.all())
bot.start_time = datetime.now()

@bot.event
async def on_shard_connect(shard_id):
    await SettingsDataBase.create_db_pool(bot=bot)
    logging.info(f"Пинг базы данных (#{shard_id}): {await SettingsDataBase.db_ping(self=None, bot=bot)} ms")


@bot.event
async def on_shard_ready(shard_id):
    await bot.change_presence(
        activity=disnake.Activity(type=disnake.ActivityType.custom, name='🔗 senko-bot.com/invite',
                                  state="🔗 senko-bot.com/invite"))
    logging.info(f"Шард #{shard_id} запущен")


plugins = [
    Comamnd("utils", "welcome_settings"),
    Comamnd("utils", "auto_roles"),
    Comamnd("utils", "logging"),
    Comamnd("utils", "server"),
    Comamnd("utils", "user"),
    Comamnd("utils", "banner"),
    Comamnd("utils", "avatar"),
    Comamnd("utils", "get_emoji"),
    Comamnd("moderation", "unban"),
    Comamnd("moderation", "ban"),
    Comamnd("moderation", "kick"),
    Comamnd("moderation", "unmute"),
    Comamnd("moderation", "mute"),
    Comamnd("moderation", "slowmode"),
    Comamnd("moderation", "clear"),
    Comamnd("music", "play"),
    Comamnd("music", "radio"),
    Comamnd("music", "stop"),
    Comamnd("music", "volume"),
    Comamnd("music", "skip"),
    Comamnd("music", "pause"),
    Comamnd("music", "resume"),
    Comamnd("music", "loop"),
    Comamnd("music", "playlist"),
    Comamnd("music", "shuffle"),
    Comamnd("fun", "anime"),
    Comamnd("fun", "personage"),
    Comamnd("fun", "country"),
    Comamnd("fun", "senko"),
    Comamnd("fun", "shiro"),
    Comamnd("fun", "fox"),
    Comamnd("nsfw", "nsfw"),
    Comamnd("rp", "rp"),
    Comamnd("other", "bot"),
    Comamnd("other", "help"),
    Comamnd("other", "shards")
]

if __name__ == "__main__":
    bot.load_extension(f"admin")

    for filename in os.listdir("./events"):
        if filename.endswith(".py"):
            bot.load_extension(f"events.{filename[:-3]}")

    for command in plugins:
        module = importlib.import_module(command.path)
        command = disnake.ext.commands.InvokableSlashCommand(
            **module.config, func=module.command
        )
        bot.add_slash_command(command)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler('./data/bot.log'),
                            logging.StreamHandler()
                        ])

    logging.info(f"Запуск бота: {round((datetime.now() - bot.start_time).total_seconds() * 1000)} ms")

bot.run(os.environ["TOKEN"])
