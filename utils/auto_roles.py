import disnake
from disnake.ext import commands


config = {
    "name": "auto-role",
    "description": "🛠 Настройка авто ролей"
}


@commands.cooldown(4, 25, commands.BucketType.guild)
@commands.guild_only()
async def command(
        inter: disnake.CommandInteraction,
        status: str = commands.Param(name="действие",
                                     description="выбор действия для системы авто ролей",
                                     choices=["Добавить", "Удалить", "Статус"]),
        role: disnake.Role = commands.Param(name="роль",
                                            description="выбор роли для действия",
                                            default=None)
):
    if inter.channel.permissions_for(inter.guild.me).manage_roles:
        if inter.channel.permissions_for(inter.author).administrator:
            if role == None and status != "Статус":
                return await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Роль не выбрана",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )

            if status == "Статус":
                res = await inter.bot.cursor.fetchval(f"""SELECT id_roles FROM autorole_settings WHERE id_server={inter.guild.id}""")
                return await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Список выдаваемых ролей:",
                        description=' '.join('<@&{}>'.format(i) for i in res) if res is not None else "Нет",
                        color=0xf1c40f
                    ),
                    ephemeral=True
                )

            if role.position >= inter.guild.me.top_role.position:
                return await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Выбранная роль выше или такая же, как у бота.",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )

            if role == inter.guild.default_role:
                return await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Нельзя использовать `@everyone`",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )

            idServer = inter.guild.id
            conn = inter.bot.cursor
            query = f"""SELECT id_roles FROM autorole_settings WHERE id_server={idServer}"""
            res = await conn.fetchval(query)

            if res is None and status != "Добавить":
                return await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Система авто ролей не включёна!",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )

            await inter.response.defer(ephemeral=True)

            if status == "Добавить":
                if res == None:
                    async with conn.acquire() as connection:
                        tr = connection.transaction()
                        await tr.start()
                        try:
                            await connection.execute(
                                """INSERT INTO autorole_settings (id_server, id_roles) VALUES ($1, $2)""",
                                idServer, [role.id]
                            )
                        except:
                            await tr.rollback()
                            raise
                        else:
                            await tr.commit()

                        await inter.followup.send(
                            embed=disnake.Embed(
                                title=f"Роль @{role.name} успешно добавлена!",
                                color=0x2ecc71
                            )
                        )
                else:
                    if len(res) == 3:
                        return await inter.followup.send(
                            embed=disnake.Embed(
                                title="Что-то пошло не так  👀",
                                description="Нельзя добавлять больше **3-х** ролей.",
                                color=0xC31B21
                            )
                        )

                    if role.id in res:
                        return await inter.followup.send(
                            embed=disnake.Embed(
                                title="Что-то пошло не так  👀",
                                description="Данная роль уже добавлена!",
                                color=0xC31B21
                            )
                        )

                    res.append(role.id)
                    async with conn.acquire() as connection:
                        tr = connection.transaction()
                        await tr.start()
                        try:
                            await connection.execute(
                                "UPDATE autorole_settings SET id_roles = $1 WHERE id_server = $2",
                                res, idServer
                            )
                        except:
                            await tr.rollback()
                            raise
                        else:
                            await tr.commit()

                        await inter.followup.send(
                            embed=disnake.Embed(
                                title=f"Роль @{role.name} успешно добавлена!",
                                color=0x2ecc71
                            )
                        )

            elif status == "Удалить":
                if role.id in res:
                    res.remove(role.id)
                    async with conn.acquire() as connection:
                        tr = connection.transaction()
                        await tr.start()
                        try:
                            if len(res) != 0:
                                await connection.execute(
                                    "UPDATE autorole_settings SET id_roles = $1 WHERE id_server = $2",
                                    res, idServer
                                )
                            else:
                                await connection.execute(
                                    f"""DELETE FROM autorole_settings WHERE id_server={idServer}"""
                                )
                        except:
                            await tr.rollback()
                            raise
                        else:
                            await tr.commit()

                    return await inter.followup.send(
                        embed=disnake.Embed(
                            title=f"Роль @{role.name} успешно удалена!",
                            color=0xe74c3c
                        )
                    )

                else:
                    return await inter.followup.send(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Данная роль отсутствует в системе авто ролей.",
                            color=0xC31B21
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
                description="У меня нет право управлять ролями!",
                color=0xC31B21
            ),
            ephemeral=True
        )
