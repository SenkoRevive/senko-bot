import disnake
from disnake.ext import commands


config = {
    "name": "clear",
    "description": "🛡 Очистка чата"
}


@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
    inter: disnake.CommandInteraction,
    count: int = commands.Param(name="количество",
                                description="количество удаляемых сообщений",
                                min_value=1,
                                max_value=100),
    member: disnake.User = commands.Param(name="пользователь",
                                          description="удалить сообщения от выбранного пользователя",
                                          default=None)
    ):
    if inter.channel.permissions_for(inter.guild.me).manage_messages and inter.channel.permissions_for(inter.guild.me).view_channel:
        if inter.channel.permissions_for(inter.author).manage_messages:
            deleted = []
            await inter.response.defer(ephemeral=True)

            if member == None:
                try:
                    deleted = await inter.channel.purge(limit=count)
                except disnake.NotFound:
                    pass

                if len(deleted):
                    await inter.followup.send(f':white_check_mark: **{len(deleted)}** сообщений было удалено', delete_after=10)
                else:
                    await inter.followup.send(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Не найдено сообщений младше 14 дней",
                            color=0xC31B21
                        )
                    )
            else:
                def check_user(m):
                    return m.author == member

                try:
                    deleted = await inter.channel.purge(limit=count, check=check_user)
                except disnake.NotFound:
                    pass

                if len(deleted):
                    await inter.followup.send(f':white_check_mark: **{len(deleted)}** cообщения от {member.mention}, были удалены', delete_after=10)
                else:
                    await inter.followup.send(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Не найдено сообщений младше 14 дней",
                            color=0xC31B21
                        )
                    )
        else:
            await inter.send(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="У вас нет прав на управление сообщениями",
                    color=0xC31B21
                )
            )
    else:
        await inter.send(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="У меня нет права на управлением сообщений или нет доступа к каналу",
                color=0xC31B21
            )
        )