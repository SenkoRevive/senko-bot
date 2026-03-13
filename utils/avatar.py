import disnake
from disnake.ext import commands


config = {
    "name": "avatar",
    "description": "🛠 Вывод аватара пользователя"
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

    embed = disnake.Embed(
        title=f"Аватар пользователя @{member.name} \n",
        description=f"**Ссылка на аватарку:** [клик]({member.display_avatar.url})",
        colour=0xf1c40f
    )
    embed.set_image(url=member.display_avatar.url)
    embed.set_footer(text='ID пользователя: ' + str(member.id))
    await inter.response.send_message(embed=embed)