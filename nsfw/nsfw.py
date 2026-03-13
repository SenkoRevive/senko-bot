import disnake
from disnake.ext import commands

import os
import aiohttp
import asyncio
import random

load_dotenv()
session = aiohttp.ClientSession()

config = {
    "name": "nsfw",
    "description": "🔞"
}

all_category = [
    "classic",
    "creampie",
    "femdom",
    "hentai",
    "incest",
    "masturbation",
    "ero",
    "orgy",
    "elves",
    "yuri",
    "pantsu",
    "glasses",
    "cuckold",
    "blowjob",
    "boobjob",
    "footjob",
    "handjob",
    "boobs",
    "pussy",
    "ahegao",
    "uniform",
    "gangbang",
    "tentacles"
]

discord_support_url = "https://support.discord.com/hc/ru/articles/115000084051#h_adc93a2c-8fc3-4775-be02-bbdbfcde5010"

async def autocomplete(inter: disnake.CommandInteraction, string: str):
    if inter.channel.is_nsfw():
        return [i for i in all_category if string in i]
    else:
        return ["Этот канал не NSFW"]


@commands.cooldown(5, 35, commands.BucketType.user)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    category: str = commands.Param(name="категория",
                            description="категория nsfw контента",
                            autocomplete=autocomplete),
    ):
    if not inter.channel.is_nsfw():
        return await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Эту команду можно использовать только в NSFW канале!",
                color=0xC31B21
            ),
            view=disnake.ui.View().add_item(
                disnake.ui.Button(
                    label="Как настроить?",
                    url=discord_support_url
                )
            ),
            ephemeral=True
        )

    elif category.lower() not in all_category:
        return await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Вы выбрали не существующую категорию",
                color=0xC31B21
            ),
            ephemeral=True
        )

    url = "https://api.rule34.xxx//index.php?page=dapi&s=post&q=index&tags={tags}&json=1&limit=1000" + f"&api_key={os.environ['TOKEN_RULE34']}&user_id={os.environ['USERID_RULE34']}"

    try:
        async with session.get(url.format(tags=category.replace(", ", "%20").replace(" ", "_"))) as resp:
            root = await resp.json()
    except aiohttp.client_exceptions.ClientOSError as e:
        await asyncio.sleep(3 + random.randint(0, 9))
        async with session.get(url.format(tags=category.replace(", ", "%20").replace(" ", "_"))) as resp:
            root = await resp.json()

    await inter.response.send_message(
            embed=disnake.Embed(
                color=0x935CB1
            ).set_image(
                url=(root[random.randint(0, len(root) - 1)]["sample_url"])
            )
        )