import disnake
from disnake.ext import commands

import os
import aiohttp
import traceback
from dotenv import load_dotenv
from settings.settings_db import SettingsDataBase

load_dotenv()

class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def guild_log(self, embed):
        async with aiohttp.ClientSession() as webhook:
            webhook = disnake.Webhook.from_url(url=os.environ["WEBHOOK_GUILD"], session=webhook)
            await webhook.send(embed=embed)

    async def bot_log(self, embed):
        async with aiohttp.ClientSession() as webhook:
            webhook = disnake.Webhook.from_url(url=os.environ["WEBHOOK_BOT"], session=webhook)
            await webhook.send(embed=embed)

    async def error_log(self, content, file):
        async with aiohttp.ClientSession() as webhook:
            webhook = disnake.Webhook.from_url(url=os.environ["WEBHOOK_ERRORS"], session=webhook)
            await webhook.send(content=content, file=file)


    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        await self.bot_log(embed=disnake.Embed(title=f"Шард #{shard_id} подключен", color=0x2ecc71))


    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        await self.bot_log(embed=disnake.Embed(title=f"Шард #{shard_id} отключен", color=0xe74c3c))


    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        await self.bot_log(embed=disnake.Embed(title=f"Шард #{shard_id} возобновил работу", color=0xFEE75C))


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = disnake.Embed(title="Новый сервер!",
                             description=f"**Имя сервера:** {guild.name} \n"
                                         f"**Владелец:** @{guild.owner.name} (ID: {guild.owner.id}) \n"
                                         f"**Дата создания:** {guild.created_at.strftime('%d.%m.%Y')} \n"
                                         f"**Количество людей:** {guild.member_count - len(([member for member in guild.members if member.bot]))} \n"
                                         f"**Количество ботов:** {len(([member for member in guild.members if member.bot])) - 1} \n"
                                         f"**ID сервера:** {guild.id} \n"
                                         f"**Шард сервера:** {guild.shard_id} \n", colour=0x2ecc71)
        if guild.icon != None:
            embed.set_thumbnail(url=str(guild.icon.url))
        embed.set_footer(text=f'Теперь у бота {len(self.bot.guilds)} серверов!')
        await self.guild_log(embed=embed)


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await SettingsDataBase.delete_data(self=None, bot=self.bot, id_server=guild.id)

        embed = disnake.Embed(title="Удалена с сервера!",
                              description=f"**Имя сервера:** {guild.name} \n"
                                          f"**Владелец:** @{guild.owner.name} (ID: {guild.owner.id}) \n"
                                          f"**Дата создания:** {guild.created_at.strftime('%d.%m.%Y')} \n"
                                          f"**Количество людей:** {guild.member_count - len(([member for member in guild.members if member.bot]))} \n"
                                          f"**Количество ботов:** {len(([member for member in guild.members if member.bot]))} \n"
                                          f"**ID сервера:** {guild.id} \n"
                                          f"**Шард сервера:** {guild.shard_id} \n", colour=0xe74c3c)
        if guild.icon != None:
            embed.set_thumbnail(url=str(guild.icon.url))
        embed.set_footer(text=f'Теперь у бота {len(self.bot.guilds)} серверов.')
        await self.guild_log(embed=embed)

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.CommandOnCooldown):
            await inter.send(f'Не так быстро :hand_splayed:\nПопробуйте снова через {error.retry_after:.2f} секунд.', ephemeral=True)
        elif isinstance(error, commands.NoPrivateMessage):
            await inter.send(f'Нельзя использовать данную команду в личных сообщениях!', ephemeral=True)
        else:
            button = disnake.ui.Button(label="Сервер поддержки", style=disnake.ButtonStyle.url, url="https://senko-bot.com/support")
            view = disnake.ui.View()
            view.add_item(button)

            embed = disnake.Embed(title="Что-то пошло не так  👀",
                                  description=f"Вы наткнулись на **неожиданную ошибку** <:SenkoFlustered:981465317287018546> \n"
                                              f"Попробуйте активировать команду снова. \n \n"
                                              f"> ⚠️  Если данная ошибка останется, пожалуйста обратитесь на наш сервер поддержки!",
                                  colour=0x992d22)
            await inter.send(embed=embed, ephemeral=True, view=view)

            if isinstance(inter.channel, disnake.abc.PrivateChannel):
                info_id = "ID-пользователя"
                ids = inter.author.id
            else:
                info_id = "ID-сервера"
                ids = inter.guild.id

            f = open(f'./data/error_traceback_{ids}.txt', 'w')
            f.write(str(''.join(traceback.format_exception(type(error), error, error.__traceback__))))
            f.close()

            arguments = {option['name']: option['value'] for option in
                         inter.data.get('options', [])} if inter.data else 'Нет'
            await self.error_log(content=f'Ошибка в команде `/{inter.application_command.qualified_name if inter.application_command else "Неизвестная команда"}`\nАргументы: `{arguments}`\n{info_id}: `{ids}`', file=disnake.File(f"./data/error_traceback_{ids}.txt"))

            os.remove(f"./data/error_traceback_{ids}.txt")


def setup(bot):
    bot.add_cog(BotEvents(bot))