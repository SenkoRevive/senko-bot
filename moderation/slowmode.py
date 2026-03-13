import disnake
from disnake.ext import commands


config = {
    "name": "slowmode",
    "description": "🛡 Добавить медленный режим"
}


@commands.cooldown(5, 30, commands.BucketType.user)
@commands.guild_only()
async def command(
        inter: disnake.CommandInteraction,
        hour: int = commands.Param(name="часы",
                                   description="время задержки в часах",
                                   min_value=0,
                                   max_value=6,
                                   default=0),
        minutes: int = commands.Param(name="минуты",
                                      description="время задержки в минутах",
                                      min_value=0,
                                      max_value=360,
                                      default=0),
        seconds: int = commands.Param(name="секунды",
                                      description="время задержки в секундах",
                                      min_value=0,
                                      max_value=21600,
                                      default=0),
):
    if inter.channel.permissions_for(inter.guild.me).manage_channels:
        if inter.channel.permissions_for(inter.author).manage_channels:
            time = hour * 3600 + minutes * 60 + seconds
            if time == 0:
                await inter.channel.edit(slowmode_delay=0)
                await inter.response.send_message(f"Убран медленный режим!", delete_after=5)
            elif time <= 21600:
                await inter.channel.edit(slowmode_delay=time)
                await inter.response.send_message(f"Установлен медленный режим на {time} секунд(-ы)!", delete_after=5)
            else:
                await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Время не может быть больше 6 часов!",
                        color=0xC31B21
                    ),
                    ephemeral=True
                )
        else:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="У вас нет прав на управление канала!",
                    color=0xC31B21
                ),
                ephemeral=True
            )
    else:
        await inter.response.send_message(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="У меня нет прав на управление каналом!",
                color=0xC31B21
            ),
            ephemeral=True
        )
