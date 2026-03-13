import disnake
import disnake.ext.commands as commands

import aiohttp


session = aiohttp.ClientSession()

config = {
    "name": "shiro",
    "description": "✨ Посмотри на фотографии Широ"
}


@commands.cooldown(5, 30, commands.BucketType.user)
async def command(
    inter: disnake.CommandInteraction,
    ):
    url = "https://purrbot.site/api/img/sfw/shiro/img"
    async with session.get(
            url.format()
    ) as resp:
        try:
            root = await resp.json()
        except:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Команда временно не доступна! Повторите чуть позже.",
                    color=0xC31B21
                ),
                ephemeral=True
            )

    await inter.response.send_message(
        embed=disnake.Embed(
            color=0xd8833a
        ).set_image(
            url=(root["link"])
        )
    )