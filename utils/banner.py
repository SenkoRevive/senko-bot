import disnake
from disnake.ext import commands


config = {
    "name": "banner",
    "description": "🛠 Вывод баннера пользователя"
}


@commands.cooldown(5, 30, commands.BucketType.user)
async def command(
    inter: disnake.CommandInteraction,
    member: disnake.User = commands.Param(name="пользователь",
                                          description="отправит аватар выбранного пользователя",
                                          default=None)
    ):
    if member == None:
        member = inter.author

    member = await inter.bot.fetch_user(member.id)

    if member.banner:
        embed = disnake.Embed(
            title=f"Баннер пользователя @{member.name} \n",
            description=f"**Ссылка на баннер:** [клик]({member.banner.url})",
            colour=0xf1c40f
        )
        embed.set_image(url=member.banner.url)
        embed.set_footer(text='ID пользователя: ' + str(member.id))
        await inter.response.send_message(embed=embed)
    elif member.accent_color:
        embed = disnake.Embed(
            title=f"**Баннер пользователя:** @{member.name} \n",
            description=f"**Цвет баннера:** **{member.accent_color}**",
            colour=0xf1c40f
        )
        embed.set_footer(text='ID пользователя: ' + str(member.id))
        await inter.response.send_message(embed=embed)
    else:
        await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="У пользователя нет кастомного баннера.",
                    color=0xC31B21
                ),
                ephemeral=True
            )