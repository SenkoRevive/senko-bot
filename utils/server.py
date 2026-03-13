import disnake
from disnake.ext import commands

import time
from pytz import timezone


config = {
    "name": "server",
    "description": "🛠 Информация о сервере"
}

verif_level = {
    "none": "Нет",
    "low": "Низкий",
    "medium": "Средний",
    "high": "Высокий",
    "highest": "Очень высокий"
}


@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    ):
    view = ServerInfoView(inter=inter, author=inter.author)
    await inter.response.send_message(embed=view.embed, view=view)
    view.message = await inter.original_message()

class ServerInfoView(disnake.ui.View):
    def __init__(self, inter: disnake.Interaction, author: disnake.Member):
        self.author = author
        super().__init__(timeout=60)

        text_button = ["Роли на сервере", "Эмодзи на сервере"]
        self.dict_button = {}

        for text in text_button:
            _ = disnake.ui.Button(label=text, style=disnake.ButtonStyle.gray)
            _.callback = self.callback
            self.add_item(
                _
            )
            self.dict_button[_.custom_id] = _

        self.embed = disnake.Embed(
                description=f'**Информация о сервере** **{inter.guild.name}**\n'
                                f'\n'
                                f'**Участники:**\n'
                                f'<:members_discord:1189917067332296724> Всего пользователей: **{inter.guild.member_count}**\n'
                                f'<:member_discord:1189917015234854942> Людей: **{inter.guild.member_count - len(([member for member in inter.guild.members if member.bot]))}**\n'
                                f'<:applicationbot_discord:1189917261046218812> Ботов: **{len(([member for member in inter.guild.members if member.bot]))}**\n'
                                f'\n'
                                f'**Статистика активности на сервере:**\n'
                                f'<:1_:1036556916765229056> В сети: **{len(list(filter(lambda m: str(m.status) == "online", inter.guild.members)))}**\n'
                                f'<:2_:1036556989486084106> Не активны: **{len(list(filter(lambda m: str(m.status) == "idle", inter.guild.members)))}**\n'
                                f'<:3_:1036557017126551612> Не беспокоить: **{len(list(filter(lambda m: str(m.status) == "dnd", inter.guild.members)))}**\n'
                                f'<:4_:1036557041168289822> Оффлайн: **{len(list(filter(lambda m: str(m.status) == "offline", inter.guild.members)))}**\n'
                                f'\n'
                                f'**Каналы:**\n'
                                f'<:channel_discord:1189919274563801239> Текстовые: **{len(inter.guild.text_channels)}**\n'
                                f'<:voicechannel_discord:1189919084268228639> Голосовые: **{len(inter.guild.voice_channels)}**\n'
                                f'<:category_discord:1189918880748019803> Категории: **{len(inter.guild.categories)}**\n'
                                f'\n'
                                f"<:5_:1074276043579469845> **Бусты:** \n"
                                f'Количество бустов: **{inter.guild.premium_subscription_count}**\n'
                                f'\n'
                                f'<:security_discord:1189925770987049072> **Уровень безопасности:** \n'
                                f'{verif_level[str(inter.guild.verification_level)]}\n'
                                f'\n'
                                f'<:events_discord:1189925415331037255> **Дата создания:**\n {"<t:{}:f>".format(int(time.mktime(inter.guild.created_at.astimezone(timezone("Europe/Moscow")).timetuple())))} \n'
                                f'\n'
                                f'<:owner_discord:1189925366706479134> **Владелец:**\n{inter.guild.owner.mention}\n',
                    color=0xf1c40f)
        self.embed.set_footer(text=f'ID сервера: {inter.guild.id}')
        if inter.guild.icon != None:
            self.embed.set_thumbnail(url=str(inter.guild.icon.url))
        if inter.guild.banner != None:
            self.embed.set_image(url=inter.guild.banner.url)

    async def callback(self, interaction: disnake.Interaction):
        if interaction.user.id == self.author.id:
            input_name_button = self.dict_button[interaction.data.custom_id].label
            if "Роли на сервере" == input_name_button:
                embed = disnake.Embed(title="Роли на сервере:",
                                      description=f'{"Нет" if len(interaction.guild.roles) < 1 else " ".join([str(r.mention) for r in interaction.guild.roles][1:])}',
                                      color=0xf1c40f)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            elif "Эмодзи на сервере" == input_name_button:
                embed = disnake.Embed(title="Эмодзи сервера:",
                                      description=f'{"Нет" if len(interaction.guild.emojis) < 1 else " ".join([str(disnake.utils.get(interaction.guild.emojis, name=r.name)) for r in interaction.guild.emojis])}',
                                      color=0xf1c40f)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Команду активировал другой пользователь!",
                    color=0xC31B21
                ),
                ephemeral=True
            )

    async def on_timeout(self):
        await self.message.edit(embed=self.embed, view=None)