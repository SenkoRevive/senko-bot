import disnake
from disnake.ext import commands


config = {
    "name": "ban",
    "description": "🛡 Заблокировать пользователя"
}

choices_delete_message = {
    "Ничего не удалять": 0,
    "Удалить написанное пользователем за последний час": 3600,
    "Удалить написанное пользователем за последние 6 часов": 21600,
    "Удалить написанное пользователем за последние 12 часов": 43200,
    "Удалить написанное пользователем за последние 24 часа": 86400,
    "Удалить написанное пользователем за последние 3 дня": 259200,
    "Удалить написанное пользователем за последние 7 дней": 604800
}

async def autocomplete(inter: disnake.CommandInteraction, string: str):
    return [i for i in list(choices_delete_message.keys()) if string in i]


@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    member: disnake.User = commands.Param(name="пользователь",
                                            description="заблокировать выбранного пользователя"),
    reason: str = commands.Param(name="причина",
                                 description="причина наказания",
                                 default="Причина не указана!",
                                 max_length=400),
    choices_dm: str = commands.Param(name="удаление-сообщений",
                                  description="сколько недавних сообщений пользователя нужно удалить",
                                  autocomplete=autocomplete),
    send_dm: str = commands.Param(name="уведомление",
                                   description="cообщить пользователю о наказании в лс",
                                   choices=["Сообщить", "Не сообщать"],
                                   default="Не сообщать"),
    ):
    if inter.channel.permissions_for(inter.guild.me).ban_members:
        if inter.channel.permissions_for(inter.author).ban_members:
            if choices_dm.lower() in {key.lower(): value for key, value in choices_delete_message.items()}:
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


                                await member.ban(clean_history_duration=choices_delete_message[choices_dm], reason=reason)
                                embed = disnake.Embed(
                                    title="Заблокирован пользователь!",
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
                                        description="Нельзя блокировать самого себя / бота!",
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
                    await inter.guild.ban(user=member, clean_history_duration=0, reason=reason)
                    embed = disnake.Embed(
                        title="Заблокирован пользователь!",
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
                        description="Вы выбрали не существующий аргумент `удаление-сообщений`",
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