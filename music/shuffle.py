import disnake
from disnake.ext import commands

from random import shuffle


config = {
    "name": "shuffle",
    "description": "🎶 Перемешивание треков в плейлисте"
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

    if len(player.queue) >= 3:
        shuffle(player.queue)
        await inter.send(
            embed=disnake.Embed(
                title=f"🔀  Плейлист был перемешан",
                color=disnake.Color.from_rgb(227, 182, 37)
            ), ephemeral=True)
    else:
        await inter.send(
            embed=disnake.Embed(
                title=f"🔀  В плейлисте меньше 3-х треков",
                color=0xC31B21
            ), ephemeral=True)
