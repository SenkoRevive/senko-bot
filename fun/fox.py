import disnake
import disnake.ext.commands as commands

import aiohttp
from random import randint


session = aiohttp.ClientSession()

config = {
    "name": "fox",
    "description": "✨ Просмотр фотографий лисиц"
}


@commands.cooldown(5, 30, commands.BucketType.user)
async def command(
    inter: disnake.CommandInteraction,
    ):
    id = randint(1, 123)
    url = f"https://randomfox.ca/images/{id}.jpg"
    await inter.response.send_message(
        embed=disnake.Embed(
            title=f"🦊 Картинка под номером: {id}",
            color=0xd8833a
        ).set_image(
            url=url
        )
    )