import disnake
from disnake.ext import commands

from settings.settings_music import Players


config = {
    "name": "skip",
    "description": "🎶 Пропуск трека(-ов)"
}


@commands.guild_only()
@commands.cooldown(5, 30, commands.BucketType.user)
async def command(
        inter: disnake.CommandInteraction,
        number: int = commands.Param(name="количество",
                                     description="число пропускаемых треков",
                                     default=1),
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

    if len(player.queue) >= number:
        del player.queue[0:number]
        await player.stop()
    else:
        await Players.destroy_player(self=None, player=player, bot=inter.bot, state=True)

    await inter.send(
        embed=disnake.Embed(
            title=f"⏭️  Пропуск треков (`{number}`)",
            color=disnake.Color.from_rgb(227, 182, 37)
        ), ephemeral=True)
    