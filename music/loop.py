import disnake
from disnake.ext import commands


config = {
    "name": "loop",
    "description": "🎶 Настройка режима повтора"
}


@commands.guild_only()
@commands.cooldown(5, 30, commands.BucketType.user)
async def command(
        inter: disnake.CommandInteraction
):
    await inter.response.defer(ephemeral=True)
    player = inter.guild.voice_client

    if not player:
        return await inter.followup.send(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description=f"Музыка сейчас не проигрывается",
                color=0xC31B21
            )
        )

    if inter.author.voice is None:
        return await inter.followup.send(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Вы не подключены к голосовому каналу!",
                color=0xC31B21
            ),
            delete_after=10
        )

    if inter.author.voice.channel != inter.guild.voice_client.channel:
        return await inter.followup.send(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description=f"Вы должны находиться в голосовом канале с ботом для управление музыкой",
                color=0xC31B21
            )
        )

    if player.current:
        if player.current.stream:
            return await inter.send(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Режим повтора отсутствует для радиостанций",
                    color=0xC31B21
                ),
                delete_after=10
            )

    if player.loop is False:
        player.loop = True
        await inter.followup.send(
            embed=disnake.Embed(
                title=f"🔁  Включен режим повтора для текущего трека",
                color=disnake.Color.from_rgb(227, 182, 37)
            ), ephemeral=True)
    else:
        player.loop = False
        await inter.followup.send(
            embed=disnake.Embed(
                title=f"🔁  Выключен режим повтора",
                color=disnake.Color.from_rgb(227, 182, 37)
            ), ephemeral=True)
