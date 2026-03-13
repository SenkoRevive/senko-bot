import disnake
from disnake.ext import commands


config = {
    "name": "unmute",
    "description": "🛡 Размьют пользователя"
}


@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    member: disnake.User = commands.Param(name="пользователь",
                                          description="рамьютить выбранного пользователя"),
    reason: str = commands.Param(name="причина",
                                 description="причина отмены наказания",
                                 default="Причина не указана!")
    ):
    if inter.channel.permissions_for(inter.guild.me).moderate_members:
        if inter.channel.permissions_for(inter.author).moderate_members:
            if inter.guild.get_member(member.id):
                if member.current_timeout != None:
                    if member.top_role.position >= inter.author.top_role.position and not inter.guild.owner or not member.top_role.position >= inter.guild.me.top_role.position:
                        await member.timeout(duration=None, reason=reason)
                        embed = disnake.Embed(
                            title="Размьючен пользователь!",
                            description=f"> **Пользователь:** {member.mention} \n"
                                        f"> **Модератор:** {inter.author.mention} \n"
                                        f"> **Причина:** {reason} \n",
                            color=0x2ecc71
                        )
                        embed.set_footer(text='ID пользователя: ' + str(member.id))
                        embed.set_thumbnail(url=member.display_avatar.url)
                        await inter.response.send_message(embed=embed)
                    else:
                        await inter.response.send_message(
                            embed=disnake.Embed(
                                title="Что-то пошло не так  👀",
                                description="У пользователя выше или такая же роль как у вас / бота!",
                                color=0xC31B21
                            ),
                            ephemeral=True
                        )
                else:
                    await inter.response.send_message(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Пользователь не в мьюте.",
                            color=0xC31B21
                        ),
                        ephemeral=True
                    )
            else:
                await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Пользователя нет на сервере!",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )
        else:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="У вас нет права на модерацию участников.",
                    color=0xC31B21
                ),
                ephemeral=True
            )
    else:
        await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="У меня нет права на модерацию участников.",
                color=0xC31B21
            ),
            ephemeral=True
        )