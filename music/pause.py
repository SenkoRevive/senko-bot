import disnake
from disnake.ext import commands


config = {
    "name": "pause",
    "description": "🎶 Приостановка проигрывания трека"
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

    if player.paused:
        return await inter.followup.send(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description=f"Проигрывание уже приостановлено",
                color=0xC31B21
            )
        )

    await player.pause()
    await inter.send(
        embed=disnake.Embed(
            title=f"⏸️  Пауза",
            color=disnake.Color.from_rgb(227, 182, 37)
        ), ephemeral=True)
