import disnake
from disnake.ext import commands

import json
import time
from pytz import timezone

config = {
    "name": "user",
    "description": "🛠 Информация о пользователе"
}

t_status = {
    "online": "<:1_:1036556916765229056> Онлайн",
    "idle": "<:2_:1036556989486084106> Не активен",
    "dnd": "<:3_:1036557017126551612> Не беспокоить",
    "offline": "<:4_:1036557041168289822> Оффлайн"
}

t_activity = {
    "Playing": "Играет в",
    "Streaming": "Стримит",
    "Listening": "Слушает",
    "Watching": "Смотрит",
    "Custom": "Кастомное:",
    "Competing": "Соревнуется",
    "Нет": "Нет"
}

t_userflags = {
    "staff": "<:staff_discord:1189605182175186994>",
    "partner": "<:partner_discord:1189605355081191424>",
    "hypesquad": "<:hypesquad_discord:1189605697894236170>",
    "bug_hunter": "<:bughunterlv1_discord:1189606094457286808>",
    "hypesquad_bravery": "<:bravery_discord:1189606366835388466>",
    "hypesquad_brilliance": "<:brillance_discord:1189606592295993344>",
    "hypesquad_balance": "<:balance_discord:1189606789453455400>",
    "early_supporter": "<:earlysupporter_discord:1189607215972229271>",
    "bug_hunter_level_2": "<:bughunterlv2_discord:1189607416921341953>",
    "verified_bot_developer": "<:verifledev_discord:1189608759748739203>",
    "discord_certified_moderator": "<:certifiedmoderator_discord:1189609236502675517>",
    "active_developer": "<:activedev_discord:1189610235783032882>",
    "verified_bot": "<:verified_app1:1245406940818046996><:verified_app2:1245406989673037884><:verified_app3:1245407037777641533>"
}

with open("data/permission.json", encoding="utf-8") as f:
    permission = json.load(f)


@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
        inter: disnake.CommandInteraction,
        member: disnake.User = commands.Param(name="пользователь",
                                              description="отправит аватар выбранного пользователя",
                                              default=None)
):
    if member == None:
        member = inter.author
    user = await inter.bot.fetch_user(member.id)
    member = inter.guild.get_member(member.id)

    if member == None:
        return await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Пользователя нет на сервере!",
                color=0xC31B21
            ),
            ephemeral=True
        )

    embed = disnake.Embed(color=0xf1c40f,
                          description=f"**Информация о {member.mention}**\n"
                                      f"\n"
                                      f"**Зарегистрирован:** {'<t:{}:f>'.format(int(time.mktime(member.created_at.astimezone(timezone('Europe/Moscow')).timetuple())))} \n"
                                      f"**Присоединился:** {'<t:{}:f>'.format(int(time.mktime(member.joined_at.astimezone(timezone('Europe/Moscow')).timetuple())))}\n"
                                      f"**Статус:** {t_status[str(member.status)]}\n"
                                      f"**Активность:** {t_activity[str(member.activity.type).split('.')[-1].title() if member.activity else 'Нет']} {'' if member.activity is None or member.activity.name is None else member.activity.name}\n"
                                      f"**Роли {'[{}]'.format(len(member.roles) - 1)}:** {' '.join([r.mention for r in member.roles][1:]) if member.roles[1:] else 'Нет'}\n"
                                      f"**Значки:** {' '.join([t_userflags[flag.name] for flag in user.public_flags.all()] or ['Нет'])}\n"
                                      f"**Права:** \n{'Администратор' if member.guild_permissions.administrator else ', '.join([permission.get(str(p[0]).replace('_', ' ').title(), 'Неизвестно право') for p in member.guild_permissions if p[1]])}\n"
                          )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text='ID пользователя: ' + str(member.id))
    if user.banner is not None:
        embed.set_image(url=user.banner.url)
    await inter.response.send_message(embed=embed)
