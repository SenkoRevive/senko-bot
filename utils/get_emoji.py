import disnake
from disnake.ext import commands


config = {
    "name": "get-emoji",
    "description": "🛠 Преобразование эмодзи в картинку"
}


@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    emoji: str = commands.Param(name="эмодзи",
                                description="выберите эмодзи")
    ):
    try:
        url = f"https://cdn.discordapp.com/emojis/{int(emoji.replace('>', '').split(':')[2])}"
        embed = disnake.Embed(
            title=f"**Изображение эмодзи** `:{emoji.replace('<', '').split(':')[1]}:`\n",
            description=f"**Ссылка:** [клик]({url})",
            colour=0xf1c40f
        )
        if emoji.replace('<', '')[0] == "a":
            embed.set_image(url=url + ".gif")
        else:
            embed.set_image(url=url + ".png")
        await inter.response.send_message(embed=embed)

    except:
        await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Укажите кастомный эмодзи",
                color=0xC31B21
            ),
            ephemeral=True
        )