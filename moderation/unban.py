import disnake
from disnake.ext import commands


config = {
    "name": "unban",
    "description": "🛡 Разблокировать пользователя"
}


@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
        inter: disnake.CommandInteraction,
        member: disnake.User = commands.Param(name="id-пользователя",
                                              description="разблокировать выбранного пользователя"),
        reason: str = commands.Param(name="причина",
                                     description="причина отмены наказания",
                                     default="Причина не указана!",
                                     max_length=400)
):
    if inter.channel.permissions_for(inter.guild.me).ban_members:
        if inter.channel.permissions_for(inter.author).ban_members:
            try:
                await inter.guild.unban(member, reason=reason)
                embed = disnake.Embed(
                    title="Разблокирован пользователь!",
                    description=f"> **Пользователь:** {member.mention} \n"
                                f"> **Модератор:** {inter.author.mention} \n"
                                f"> **Причина:** {reason} \n",
                    color=0x2ecc71
                )
                embed.set_footer(text='ID пользователя: ' + str(member.id))
                embed.set_thumbnail(url=member.display_avatar.url)
                return await inter.response.send_message(embed=embed)
            except:
                await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Пользователь отсутствует в бан листе!",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )
        else:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="У вас нет прав на блокировку участников.",
                    color=0xC31B21
                ),
                ephemeral=True
            )
    else:
        await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="У меня нет прав на блокировку участников.",
                color=0xC31B21
            ),
            ephemeral=True
        )
