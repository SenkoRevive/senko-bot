import disnake
from disnake.ext import commands

import aiohttp
import os
import re
import json


config = {
    "name": "welcome-settings",
    "description": "🛠 Настройка приветствий пользователей"
}


class MethodSend(disnake.ui.StringSelect):
    def __init__(self, channel, inter, res):
        self.res = res
        self.inter = inter
        self.channel = channel
        options = [
            disnake.SelectOption(label="Текстовой канал", description="Отправлять приветствия в текстовой канал",
                                 emoji="<:channel_discord:1189919274563801239>"),
            disnake.SelectOption(label="Личные сообщения", description="Отправлять приветствия в личные сообщения",
                                 emoji="<:member_discord:1189917015234854942>")
        ]

        super().__init__(
            placeholder="Сделайте выбор",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="dropdown_welcome",
        )

    async def callback(self, inter: disnake.MessageInteraction):
        return await inter.response.send_modal(WelcomeFields(inter.values[0], self.channel, self.inter, self.res))


class DropDownView(disnake.ui.View):
    def __init__(self, channel, inter, res):
        self.res = res
        self.inter = inter
        self.channel = channel
        super().__init__(timeout=60.0)

        self.add_item(MethodSend(channel, inter, res))

    async def on_timeout(self):
        msg = await self.inter.original_response()
        embed = disnake.Embed(title=f"Время ожидания истекло!", colour=0xd65845)
        embed.set_footer(text="")
        await msg.edit(embed=embed, view=None)

class WelcomeFields(disnake.ui.Modal):
    def __init__(self, dropdown_inter, channel, inter, res):
        self.res = res
        self.inter = inter
        self.channel = channel
        self.dropdown_inter = dropdown_inter
        components = [
            disnake.ui.TextInput(
                label="Титульный текст",
                custom_id="title",
                style=disnake.TextInputStyle.short,
                min_length=3,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Основной текст",
                placeholder="<#id-канала> - указать канал в тексте",
                custom_id="description",
                style=disnake.TextInputStyle.paragraph,
                min_length=10,
                max_length=500
            )
        ]
        super().__init__(
            title="Заполните все поля 🦊",
            custom_id="modal_welcome",
            components=components,
        )

    async def callback(self, inter: disnake.ModalInteraction):
        text_values = inter.text_values
        conn = inter.bot.cursor

        msg = await self.inter.original_response()

        tag_description = re.sub("^\s+|\n|\r|\s+$", ' ', text_values["description"])
        json_data = [{"title": f"{text_values['title']}", "description": f"{tag_description}"}]

        try:
            await inter.response.send_message(content="")
        except:
            pass

        if self.dropdown_inter == "Текстовой канал":
            if self.res == None or self.res == ".":
                webhook = await self.channel.create_webhook(name="Система приветствий", reason="Вебхук для системы приветствий", avatar=inter.guild.me.avatar)
                async with conn.acquire() as connection:
                    tr = connection.transaction()
                    await tr.start()
                    try:
                        if self.res != ".":
                            await connection.execute(
                                """INSERT INTO welcome_settings (id_server, method_send, content) VALUES ($1, $2, $3)""",
                                inter.guild.id, webhook.url, json.dumps(json_data)
                            )
                        else:
                            await connection.execute(
                                """UPDATE welcome_settings SET method_send = $1, content = $2 WHERE id_server = $3""",
                                webhook.url, json.dumps(json_data), self.inter.guild.id
                            )
                    except:
                        await tr.rollback()
                        raise
                    else:
                        await tr.commit()

                await msg.edit(
                    embed=disnake.Embed(
                        title=f"Система приветствий активирована",
                        color=0x2ecc71
                    ),
                    view=None
                )
            else:
                try:
                    async with aiohttp.ClientSession() as webhook:
                        webhook = disnake.Webhook.from_url(url=self.res, session=webhook, bot_token=os.environ["TOKEN"])
                        await webhook.edit(channel=self.channel)
                        await msg.edit(
                            embed=disnake.Embed(
                                title=f"Система приветствий обновлена",
                                color=0x2ecc71
                            ),
                            view=None
                        )
                except:
                    async with conn.acquire() as connection:
                        tr = connection.transaction()
                        await tr.start()
                        try:
                            await connection.execute(
                                f"""DELETE FROM welcome_settings WHERE id_server={inter.guild.id}""",
                            )
                        except:
                            await tr.rollback()
                            raise
                        else:
                            await tr.commit()

                    await msg.edit(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Вебхук не найден",
                            color=0xC31B21
                        ),
                        view=None
                    )
        else:
            if self.res == None:
                async with conn.acquire() as connection:
                    tr = connection.transaction()
                    await tr.start()
                    try:
                        await connection.execute(
                            """INSERT INTO welcome_settings (id_server, method_send, content) VALUES ($1, $2, $3)""",
                            inter.guild.id, ".", json.dumps(json_data)
                        )
                    except:
                        await tr.rollback()
                        raise
                    else:
                        await tr.commit()

                await msg.edit(
                    embed=disnake.Embed(
                        title=f"Система приветствий активирована",
                        color=0x2ecc71
                    ),
                    view=None
                )
            else:
                async with conn.acquire() as connection:
                    tr = connection.transaction()
                    await tr.start()
                    try:
                        await connection.execute(
                            """UPDATE welcome_settings SET method_send = $1, content = $2 WHERE id_server = $3""",
                            ".", json.dumps(json_data), self.inter.guild.id
                        )
                    except:
                        await tr.rollback()
                        raise
                    else:
                        await tr.commit()

                await msg.edit(
                    embed=disnake.Embed(
                        title=f"Система приветствий обновлена",
                        color=0x2ecc71
                    ),
                    view=None
                )


@commands.cooldown(3, 35, commands.BucketType.guild)
@commands.guild_only()
async def command(
        inter: disnake.CommandInteraction,
        status: str = commands.Param(name="действие",
                                     description="выбор действия",
                                     choices=["Включить", "Обновить", "Выключить"]),
        channel: disnake.TextChannel = commands.Param(name="канал",
                                                      description="выбор канала для действия")
):
    if channel.permissions_for(inter.guild.me).manage_webhooks:
        if channel.permissions_for(inter.author).administrator:
            conn = inter.bot.cursor
            res = await conn.fetchval(f"""SELECT method_send FROM welcome_settings WHERE id_server={inter.guild.id}""")

            if status != "Включить" and res is None:
                return await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Приветствие пользователей не включёно",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )

            await inter.response.defer(ephemeral=True)

            if status == "Включить" or status == "Обновить":
                embed = disnake.Embed(
                    title=f"Выберите способ отправки приветствия:",
                    color=0xFEE75C
                )
                embed.set_footer(text="Время ожидания 60 секунд")
                await inter.followup.send(embed=embed, view=DropDownView(channel, inter, res))
            else:
                conn = inter.bot.cursor
                res = await conn.fetchval(f"""SELECT method_send FROM welcome_settings WHERE id_server={inter.guild.id}""")

                try:
                    async with aiohttp.ClientSession() as webhook:
                        webhook = disnake.Webhook.from_url(url=res, session=webhook, bot_token=os.environ["TOKEN"])
                        await webhook.delete()
                except:
                    pass

                async with conn.acquire() as connection:
                    tr = connection.transaction()
                    await tr.start()
                    try:
                        await connection.execute(
                            f"""DELETE FROM welcome_settings WHERE id_server={inter.guild.id}""",
                        )
                    except:
                        await tr.rollback()
                        raise
                    else:
                        await tr.commit()

                return await inter.followup.send(
                    embed=disnake.Embed(
                        title=f"Система приветствий отключена",
                        color=0xe74c3c
                    )
                )
        else:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="У вас нет прав администратора!",
                    color=0xf1c40f
                ),
                ephemeral=True
            )
    else:
        await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="У меня нет право управлением вебхуками!",
                color=0xC31B21
            ),
            ephemeral=True
        )