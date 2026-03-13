import disnake
from disnake.ext import commands

import time
import json
import aiohttp
from pytz import timezone


class LoggingEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_webhook(self, embed, url, id_server, content=None):
        try:
            async with aiohttp.ClientSession() as webhook:
                webhook = disnake.Webhook.from_url(url=url, session=webhook)
                await webhook.send(content=content, embed=embed)
        except:
            async with self.bot.cursor.acquire() as connection:
                tr = connection.transaction()
                await tr.start()
                try:
                    await self.bot.cursor.execute(
                        f"""DELETE FROM logging_settings WHERE id_server={id_server}""",
                    )
                except:
                    await tr.rollback()
                    raise
                else:
                    await tr.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        query = f"""SELECT webhook_url FROM logging_settings WHERE id_server={member.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            if not member.bot:
                embed = disnake.Embed(title=":pencil: Журнал Аудита | Новый пользователь",
                                      description=f"> **Пользователь:** {member.mention} (@{member.name}) \n"
                                                  f"> **Аккаунт создан:** {'<t:{}:R>'.format(int(time.mktime(member.created_at.astimezone(timezone('Europe/Moscow')).timetuple())))} (`{member.created_at.astimezone(timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M:%S')}`)\n"
                                                  f"> **Пользователей стало:** {'{}'.format(member.guild.member_count)}",
                                      color=0x2ecc71)
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f'ID аккаунта: {member.id}')
                await self.send_webhook(embed=embed, url=url, id_server=member.guild.id)

            else:
                entry = list(await member.guild.audit_logs(limit=1, action=disnake.AuditLogAction.bot_add).flatten())[0]

                if entry.target.id == member.id:
                    embed = disnake.Embed(title=":pencil: Журнал Аудита | Добавлен бот",
                                          description=f"> **Бот:** {member.mention} (@{member.display_name}#{member.discriminator})\n"
                                                      f"> **Добавил бота:** {entry.user.mention} (@{entry.user.name}) \n"
                                                      f"> **Аккаунт создан:** {'<t:{}:R>'.format(int(time.mktime(member.created_at.astimezone(timezone('Europe/Moscow')).timetuple())))} (`{member.created_at.astimezone(timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M:%S')}`)\n"
                                                      f"> **Участников стало:** {'{}'.format(member.guild.member_count)}",
                                          color=0x2ecc71)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f'ID аккаунта: {member.id}')
                    await self.send_webhook(embed=embed, url=url, id_server=member.guild.id)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={member.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            entry = list(await member.guild.audit_logs(limit=1).flatten())[0]

            if not member.bot:
                roles = ' '.join([r.mention for r in member.roles][1:])

                if entry.action == disnake.AuditLogAction.kick and entry.target == member:
                    embed = disnake.Embed(title=':pencil: Журнал Аудита | Выгнали пользователя',
                                          description=f"> **Пользователь:** {entry.target.mention} (@{entry.target.name})\n"
                                                      f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                                                      f"> **Причина:** {'Причина не указана' if entry.reason == None else entry.reason} \n"
                                                      f"> **Бывшие роли:** {'Не было' if roles == '' else roles} \n"
                                                      f"> **Осталось пользователей:** {'{}'.format(member.guild.member_count)} \n",
                                          color=0xe74c3c)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f'ID аккаунта: {entry.target.id}')
                    await self.send_webhook(embed=embed, url=url, id_server=member.guild.id)
                else:
                    embed = disnake.Embed(title=':pencil: Журнал Аудита | Вышел пользователь',
                                          description=f"> **Вышел пользователь:** {member.mention} (@{member.name})\n"
                                                      f"> **Бывшие роли:** {'Не было' if roles == '' else roles} \n"
                                                      f"> **Осталось пользователей:** {'{}'.format(member.guild.member_count)} \n",
                                          color=0xe74c3c)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f'ID аккаунта: {member.id}')
                    await self.send_webhook(embed=embed, url=url, id_server=member.guild.id)

            else:
                embed = disnake.Embed(title=':pencil: Журнал Аудита | Удалён бот',
                                      description=f"> **Бот:** {entry.target.mention} (@{member.display_name}#{member.discriminator})\n"
                                                  f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                                                  f"> **Причина:** {'Причина не указана' if entry.reason == None else entry.reason} \n"
                                                  f"> **Осталось пользователей:** {'{}'.format(member.guild.member_count)} \n",
                                      color=0xe74c3c)
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f'ID аккаунта: {entry.target.id}')
                await self.send_webhook(embed=embed, url=url, id_server=member.guild.id)


    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            entry = list(await guild.audit_logs(limit=1, action=disnake.AuditLogAction.ban).flatten())[0]

            embed = disnake.Embed(title=':pencil: Журнал Аудита | Заблокирован пользователь',
                                  description=f"> **Пользователь:** {entry.target.mention} (@{entry.target.name})\n"
                                              f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                                              f"> **Причина:** {'Причина не указана' if entry.reason == None else entry.reason} \n",
                                  color=0xe74c3c)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f'ID аккаунта: {entry.target.id}')
            await self.send_webhook(embed=embed, url=url, id_server=guild.id)


    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            entry = list(await guild.audit_logs(limit=1, action=disnake.AuditLogAction.unban).flatten())[0]

            embed = disnake.Embed(title=':pencil: Журнал Аудита | Разблокирован пользователь',
                                  description=f"> **Пользователь:** {entry.target.mention} (@{entry.target.name})\n"
                                              f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                                              f"> **Причина:** {'Причина не указана' if entry.reason == None else entry.reason} \n",
                                  color=0x2ecc71)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f'ID аккаунта: {entry.target.id}')
            await self.send_webhook(embed=embed, url=url, id_server=guild.id)


    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={before.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            mbed = disnake.Embed()
            entry = list(await before.guild.audit_logs(limit=1, action=disnake.AuditLogAction.member_update).flatten())[0]

            if before.roles != after.roles:
                entry = list(await before.guild.audit_logs(limit=1, action=disnake.AuditLogAction.member_role_update).flatten())[0]

                roles = []
                for role in before.roles:
                    if role not in after.roles:
                        roles.append(role.mention)

                if roles:
                    mbed.title = ":pencil: Журнал Аудита | Изменение ролей пользователя"
                    mbed.description = (
                        f"> **Пользователь:** {entry.target.mention} (@{entry.target.name}) \n"
                        f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                        f"> **Убранные роли:** {' '.join(roles)} \n"
                    )
                    mbed.color = 0xFEE75C

                else:
                    for role in after.roles:
                        if role not in before.roles:
                            roles.append(role.mention)

                        mbed.title = ":pencil: Журнал Аудита | Изменение ролей пользователя"
                        mbed.description = (
                            f"> **Пользователь:** {entry.target.mention} (@{entry.target.name}) \n"
                            f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                            f"> **Новые роли:** {' '.join(roles)} \n"
                        )
                        mbed.color = 0xFEE75C

            elif before.current_timeout != after.current_timeout:
                if before.current_timeout:
                    mbed.title = ':pencil: Журнал Аудита | Таймаут снят'
                    mbed.description = (
                        f"> **Пользователь:** {entry.target.mention} (@{entry.target.name}) \n"
                        f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                        f"> **Причина:** {'Причина не указана' if entry.reason == None else entry.reason} \n"
                    )
                    mbed.color = 0x2ecc71

                else:
                    mbed.title = ':pencil: Журнал Аудита | Таймаут выдан'
                    mbed.description = (
                        f"> **Пользователь:** {entry.target.mention} (@{entry.target.name}) \n"
                        f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                        f"> **Срок:** {'<t:{}:R>'.format(int(time.mktime(after.current_timeout.astimezone(timezone('Europe/Moscow')).timetuple())))} (`{after.current_timeout.astimezone(timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M:%S')}`) \n"
                        f"> **Причина:** {'Причина не указана' if entry.reason == None else entry.reason} \n"
                    )
                    mbed.color = 0xe74c3c

            elif before.nick != after.nick:
                mbed.title = ":pencil: Журнал Аудита | Изменение ника пользователя"
                mbed.description = (
                    f"> **Пользователь:** {entry.target.mention} (@{entry.target.name}) \n"
                    f"> **Старый:** `{before.nick if before.nick != None else entry.target.name}` \n"
                    f"> **Новый:** `{after.nick if after.nick != None else entry.target.name}` \n"
                )
                mbed.color = 0xFEE75C

            if mbed.description:
                mbed.set_footer(text='ID участника: ' + str(before.id))
                await self.send_webhook(embed=mbed, url=url, id_server=before.guild.id)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={member.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            mbed = disnake.Embed()

            if before.channel == after.channel:
                if before.mute != after.mute:
                    entry = list(await member.guild.audit_logs(limit=1, action=disnake.AuditLogAction.member_update).flatten())[0]

                    if before.mute:
                        mbed.title = ":pencil: Журнал Аудита | Пользователь размьючен"
                        mbed.description = (
                            f"> **Пользователь:** {entry.target.mention} (@{entry.target.name}) \n"
                            f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                            f"> **Голосовой канал:** {after.channel.mention} \n"
                        )
                        mbed.color = 0x2ecc71

                    else:
                        mbed.title = ":pencil: Журнал Аудита | Пользователь замьючен"
                        mbed.description = (
                            f"> **Пользователь:** {entry.target.mention} (@{entry.target.name}) \n"
                            f"> **Модератор:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                            f"> **Голосовой канал:** {after.channel.mention} \n"
                        )
                        mbed.color = 0xe74c3c

            else:
                if after.channel is not None:
                    mbed.title = ":pencil: Журнал Аудита | Пользователь зашёл в голосовой канал"
                    mbed.description = (
                        f"> **Пользователь:** {member.mention} \n"
                        f"> **Канал:** {after.channel.mention} \n"
                    )
                    mbed.color = 0x2ecc71

                elif after.channel is None:
                    mbed.title = ":pencil: Журнал Аудита | Пользователь покинул голосовой канал"
                    mbed.description = (
                        f"> **Пользователь:** {member.mention} \n"
                        f"> **Канал:** {before.channel.mention} \n"
                    )
                    mbed.color = 0xe74c3c

            if mbed.description:
                mbed.set_footer(text='ID участника: ' + str(member.id))
                await self.send_webhook(embed=mbed, url=url, id_server=member.guild.id)


    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={channel.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            entry = list(await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_create).flatten())[0]

            embed = disnake.Embed(title=':pencil: Журнал Аудита | Создан канал',
                                  description=f"> **Канал:** {entry.target.mention} ({entry.target.name})\n"
                                              f"> **Категория:** {'Нет' if entry.target.category is None else entry.target.category.name} \n \n"
                                              f"> **Создатель канала:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                                              f"> **Дата действия:** {'<t:{}:f>'.format(int(time.mktime(channel.created_at.astimezone(timezone('Europe/Moscow')).timetuple())))} \n",
                                  color=0x2ecc71)
            embed.set_footer(text=f'ID канала: {channel.id}')
            await self.send_webhook(embed=embed, url=url, id_server=channel.guild.id)


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={channel.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            entry = list(await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_delete).flatten())[0]

            embed = disnake.Embed(title=':pencil: Журнал Аудита | Удален канал',
                                  description=f"> **Канал:** {channel.name} \n \n"
                                              f"> **Удалил канал:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                                              f"> **Дата действия:** {'<t:{}:f>'.format(int(time.mktime(entry.created_at.astimezone(timezone('Europe/Moscow')).timetuple())))} \n",
                                  color=0xe74c3c)
            embed.set_footer(text=f'ID канала: {channel.id}')
            await self.send_webhook(embed=embed, url=url, id_server=channel.guild.id)


    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={role.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            entry = list(await role.guild.audit_logs(limit=1, action=disnake.AuditLogAction.role_create).flatten())[0]

            if entry.target.id == role.id:
                with open("data/permission.json", encoding="utf-8") as f:
                    permissions = json.load(f)

                embed = disnake.Embed(title=':pencil: Журнал Аудита | Создана роль',
                                      description=f"> **Роль:** {entry.target.mention}\n"
                                                  f"> **Создал роль:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                                                  f"> **Цвет роли:** {role.color} \n"
                                                  f"> **Права у роли:** {'Администратор' if role.permissions.administrator else ', '.join([permissions[str(p[0]).replace('_', ' ').title()] for p in role.permissions if p[1]]) or 'Нет'}",
                                      color=0x2ecc71)
                embed.set_footer(text='ID роли: ' + str(entry.target.id))
                await self.send_webhook(embed=embed, url=url, id_server=role.guild.id)


    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={role.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            entry = list(await role.guild.audit_logs(limit=1, action=disnake.AuditLogAction.role_delete).flatten())[0]

            if entry.target.id == role.id:
                with open("data/permission.json", encoding="utf-8") as f:
                    permissions = json.load(f)

                embed = disnake.Embed(title=':pencil: Журнал Аудита | Удалена роль',
                                      description=f"> **Роль:** @{role.name} \n"
                                                  f"> **Удалил роль:** {entry.user.mention} {f'(@{entry.user.name})' if entry.user.bot != True else f'(@{entry.user.display_name}#{entry.user.discriminator})'} \n"
                                                  f"> **Цвет удалённой роли:** {role.color} \n"
                                                  f"> **Права удалённой роли:** {'Администратор' if role.permissions.administrator else ', '.join([permissions[str(p[0]).replace('_', ' ').title()] for p in role.permissions if p[1]]) or 'Нет'}",
                                      color=0xe74c3c)
                embed.set_footer(text='ID роли: ' + str(entry.target.id))
                await self.send_webhook(embed=embed, url=url, id_server=role.guild.id)


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={message.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            attachments_url = []
            if message.attachments:
                for attachment in message.attachments:
                    attachments_url.append(attachment.url.replace('cdn.discordapp.com', 'media.discordapp.net'))
                    attachments_url = " ".join(attachments_url)
            else:
                attachments_url = None

            if not message.author.bot:
                embed = disnake.Embed(title=':pencil: Журнал Аудита | Удалено сообщение',
                                      description=f"> **Канал:** {message.channel.mention} ({message.channel.name}) \n"
                                                  f"> **Автор:** {message.author.mention} {f'(@{message.author.name})' if message.author.bot != True else f'(@{message.author.display_name}#{message.author.discriminator})'} \n \n"
                                                  f"> **Содержание:** ``` {message.content} ```",
                                      color=0xe74c3c)
                embed.set_footer(text='ID сообщения: ' + str(message.id))
                await self.send_webhook(embed=embed, url=url, id_server=message.guild.id, content=attachments_url)


    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, message):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={message.guild_id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            entry = list(await self.bot.get_guild(message.guild_id).audit_logs(limit=1, action=disnake.AuditLogAction.message_bulk_delete).flatten())[0]
            target_user = entry.user

            embed = disnake.Embed(title=':pencil: Журнал Аудита | Массовое удаление сообщений',
                                  description=f"> **Канал:** {self.bot.get_channel(message.channel_id).mention} ({self.bot.get_channel(message.channel_id).name}) \n"
                                              f"> **Удалил сообщения:** {target_user.mention} {f'(@{target_user.name})' if target_user.bot != True else f'(@{target_user.display_name}#{target_user.discriminator})'} \n",
                                  color=0xe74c3c)
            await self.send_webhook(embed=embed, url=url, id_server=message.guild_id)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        query = f""" SELECT webhook_url FROM logging_settings WHERE id_server={before.guild.id}"""
        url = await self.bot.cursor.fetchval(query)

        if url == None:
            pass
        else:
            if before.author.bot != True:
                if before.content != after.content:
                    embed = disnake.Embed(title=':pencil: Журнал Аудита | Изменено сообщение',
                                          description=f"> **Канал:** {before.channel.mention} ({before.channel.name}) \n"
                                                      f"> **Автор сообщения:** {before.author.mention} (@{before.author.name}) \n \n"
                                                      f"> **До:** ``` {before.content} ``` \n"
                                                      f"> **После:** ``` {after.content} ```",
                                          color=0xFEE75C)
                    embed.set_footer(text='ID сообщения: ' + str(before.id))
                    await self.send_webhook(embed=embed, url=url, id_server=before.guild.id)


def setup(bot):
    bot.add_cog(LoggingEvents(bot))