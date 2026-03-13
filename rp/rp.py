import disnake
from disnake.ext import commands

import aiohttp
import json

session = aiohttp.ClientSession()

config = {
    "name": "rp",
    "description": "🎭 Выразите свою эмоцию необычным способом"
}

with open("data/rp.json", encoding="utf-8") as f:
    all_rp = json.load(f)

async def autocomplete(inter: disnake.CommandInteraction, string: str):
    return [i for i in list(all_rp[0].keys()) if string in i]


@commands.cooldown(5, 35, commands.BucketType.user)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    category: str = commands.Param(name="категория",
                            description="категория rp контента",
                            autocomplete=autocomplete),
    member: disnake.User = commands.Param(name="пользователь", description="выбор участника")
    ):
    if category not in list(all_rp[0].keys()):
        return await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Вы выбрали не существующую категорию!",
                color=0xC31B21
            ),
            ephemeral=True
        )
    elif member.id == inter.author.id:
        return await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Нельзя указывать самого себя!",
                color=0xC31B21
            ),
            ephemeral=True
        )
    elif member.bot:
        return await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Нельзя указывать бота!",
                color=0xC31B21
            ),
            ephemeral=True
        )
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.waifu.pics/sfw/{all_rp[0][category][0]}") as response:
                try:
                    data = await response.json()
                    await inter.response.send_message(
                        embed=disnake.Embed(
                            description=f"{inter.author.mention} **{all_rp[0][category][1]}** {member.mention}",
                            color=disnake.Color.dark_grey()
                        ).set_image(
                            url=(data["url"])
                        )
                    )
                except:
                    return await inter.response.send_message(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Команда временно не доступна! Повторите чуть позже.",
                            color=0xC31B21
                        ),
                        ephemeral=True
                    )