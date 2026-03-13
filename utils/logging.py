import disnake
from disnake.ext import commands

import aiohttp
import os


config = {
    "name": "logging",
    "description": "🛠 Настройка журнала действий"
}


@commands.cooldown(3, 35, commands.BucketType.guild)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    status: str = commands.Param(name="действие",
                                 description="выбор действия для журнала",
                                 choices=["Включить", "Обновить", "Выключить"]),
    channel: disnake.TextChannel = commands.Param(name="канал",
                                                  description="выбор канала для журнала действий")
    ):
    if channel.permissions_for(inter.guild.me).manage_webhooks and channel.permissions_for(inter.guild.me).view_audit_log:
        if channel.permissions_for(inter.author).administrator:
            conn = inter.bot.cursor
            query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={inter.guild.id}"""
            res = await conn.fetchval(query)

            if status != "Включить" and res == None:
                return await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Журнал действий не включён!",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )

            await inter.response.defer(ephemeral=True)

            if status == "Включить" and res == None:
                    webhook = await channel.create_webhook(name="Журнал действий", reason="Вебхук для журнала действий", avatar=inter.guild.me.avatar)
                    await webhook.send("Проверка доступности...", delete_after=1)

                    async with conn.acquire() as connection:
                        tr = connection.transaction()
                        await tr.start()
                        try:
                            await connection.execute(
                                """INSERT INTO logging_settings (id_server, webhook_url) VALUES ($1, $2)""",
                                inter.guild.id, webhook.url
                            )
                        except:
                            await tr.rollback()
                            raise
                        else:
                            await tr.commit()

                    await inter.followup.send(
                        embed=disnake.Embed(
                            title=f"Журнал действий активирован в канале {channel.mention}",
                            color=0x2ecc71
                        )
                    )

            elif status != "Выключить" and res != None:
                try:
                    async with aiohttp.ClientSession() as webhook:
                        webhook = disnake.Webhook.from_url(url=res, session=webhook, bot_token=os.environ["TOKEN"])
                        await webhook.edit(channel=channel)
                        await inter.followup.send(
                            embed=disnake.Embed(
                                title=f"Канал для журнала действий был обновлён на {channel.mention}",
                                color=0x2ecc71
                            )
                        )
                except:
                    async with conn.acquire() as connection:
                        tr = connection.transaction()
                        await tr.start()
                        try:
                            await connection.execute(
                                f"""DELETE FROM logging_settings WHERE id_server={inter.guild.id}""",
                            )
                        except:
                            await tr.rollback()
                            raise
                        else:
                            await tr.commit()

                    return await inter.followup.send(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Вебхук не найден!",
                            color=0xC31B21
                        )
                    )

            elif status == "Выключить":
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
                                f"""DELETE FROM logging_settings WHERE id_server={inter.guild.id}""",
                            )
                        except:
                            await tr.rollback()
                            raise
                        else:
                            await tr.commit()

                    await inter.followup.send(
                        embed=disnake.Embed(
                            title=f"Журнал действий отключён!",
                            color=0xe74c3c
                        )
                    )

        else:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="У вас нет прав администратора!",
                    color=0xC31B21
                ),
                ephemeral=True
            )
    else:
        await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="У меня нет прав на просмотр журнала аудита и управлением вебхуками!",
                    color=0xC31B21
                ),
                ephemeral=True
            )