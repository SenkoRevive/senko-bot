import disnake
from disnake.ext import commands

import re
from datetime import datetime, timedelta
import time


config = {
    "name": "mute",
    "description": "🛡 Мьют пользователя"
}


def parse_time(time):
    check = re.findall(r'(\d+)([a-z])', time)
    dtime = {'d': 0, "h": 0, "m": 0, "s": 0}

    for value, unit in check:
        dtime[unit] = int(value)

    return dtime

@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    member: disnake.User = commands.Param(name="пользователь",
                                          description="замьютить выбранного пользователя"),
    mtime: str = commands.Param(name="время",
                               description="время мьюта (пример: 1h30m)"),
    reason: str = commands.Param(name="причина",
                                 description="причина наказания",
                                 default="Причина не указана!")
    ):
    if inter.guild.get_member(member.id):
        if inter.channel.permissions_for(inter.guild.me).moderate_members:
            if inter.channel.permissions_for(inter.author).moderate_members:
                if member != inter.guild.owner and member.guild_permissions.administrator != True:
                    if inter.author != member and inter.guild.me != member:
                            if member.current_timeout == None:
                                if not member.top_role.position >= inter.author.top_role.position and not member.top_role.position >= inter.guild.me.top_role.position:
                                    result = parse_time(mtime)
                                    if (result["s"] / 60 + result["m"] + result["h"] * 60 + result["d"] * 1440) < 40320:
                                       if (result["s"] / 60 + result["m"] + result["h"] * 60 + result["d"] * 1440) > 0:
                                           duration = timedelta(days=result["d"], hours=result["h"], minutes=result["m"], seconds=result["s"])
                                           time_out = '<t:{}:R>'.format(int(time.mktime((datetime.now() + duration).timetuple())))

                                           await member.timeout(duration=duration, reason=reason)

                                           embed = disnake.Embed(
                                               title="Замьючен пользователь!",
                                               description=f"> **Пользователь:** {member.mention} \n"
                                                           f"> **Модератор:** {inter.author.mention} \n"
                                                           f"> **Причина:** {reason} \n"
                                                           f"> **Мьют снимется:** {time_out}",
                                               color=0xe74c3c
                                           )
                                           embed.set_footer(text='ID пользователя: ' + str(member.id))
                                           embed.set_thumbnail(url=member.display_avatar.url)
                                           await inter.response.send_message(embed=embed)
                                       else:
                                           await inter.response.send_message(
                                               embed=disnake.Embed(
                                                   title="Что-то пошло не так  👀",
                                                   description="Указано некорректное время! (Пример: 1h30m)",
                                                   color=0xC31B21
                                               ),
                                               ephemeral=True
                                           )
                                    else:
                                        await inter.response.send_message(
                                            embed=disnake.Embed(
                                                title="Что-то пошло не так  👀",
                                                description="Нельзя замьютить человека больше 28-ми дней!",
                                                color=0xC31B21
                                            ),
                                            ephemeral=True
                                        )
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
                                        description="Пользователь в мьюте.",
                                        color=0xC31B21
                                    ),
                                    ephemeral=True
                                )
                    else:
                        await inter.response.send_message(
                            embed=disnake.Embed(
                                title="Что-то пошло не так  👀",
                                description="Нельзя мьютить самого себя / бота!",
                                color=0xC31B21
                            ),
                            ephemeral=True
                        )
                else:
                    await inter.response.send_message(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Пользователь является владельцем или администратором сервера!",
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
    else:
        await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Пользователя нет на сервере!",
                color=0xC31B21
            ),
            ephemeral=True
        )