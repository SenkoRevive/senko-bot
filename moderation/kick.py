import disnake
from disnake.ext import commands


config = {
    "name": "kick",
    "description": "🛡 Выгнать пользователя"
}


@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    member: disnake.User = commands.Param(name="пользователь",
                                            description="выгнать выбранного пользователя"),
    reason: str = commands.Param(name="причина",
                                 description="причина наказания",
                                 default="Причина не указана!",
                                 max_length=400),
    send_dm: str = commands.Param(name="уведомление",
                                   description="cообщить пользователю о наказании в лс",
                                   choices=["Сообщить", "Не сообщать"],
                                   default="Не сообщать"),
    ):
    if inter.channel.permissions_for(inter.guild.me).kick_members:
        if inter.channel.permissions_for(inter.author).kick_members:
            if inter.guild.get_member(member.id):
                if member != inter.guild.owner:
                    if inter.author != member and inter.guild.me != member:
                        if member.top_role.position >= inter.author.top_role.position and not inter.guild.owner or not member.top_role.position >= inter.guild.me.top_role.position:
                            if send_dm == "Сообщить":
                                try:
                                    dm = await member.create_dm()
                                    await dm.send(f"Вас заблокировали на сервере **{inter.guild.name}** по следующей причине: {reason}")
                                except:
                                    pass

                            await member.kick(reason=reason)
                            embed = disnake.Embed(
                                title="Выгнан пользователь!",
                                description=f"> **Пользователь:** {member.mention} \n"
                                            f"> **Модератор:** {inter.author.mention} \n"
                                            f"> **Причина:** {reason} \n",
                                color=0xe74c3c
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
                                    description="Нельзя выгонять самого себя / бота!",
                                    color=0xC31B21
                                ),
                                ephemeral=True
                            )
                else:
                    await inter.response.send_message(
                            embed=disnake.Embed(
                                title="Что-то пошло не так  👀",
                                description="Пользователь является владельцем сервера!",
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
                        description="У вас нет прав выгонять участников.",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )
    else:
        await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="У меня нет прав выгонять участников.",
                    color=0xC31B21
                ),
                ephemeral=True
            )