import json
import mafic
import asyncio

import disnake
from disnake import OptionChoice
from disnake.ext import commands

from settings.settings_music import Players

config = {
    "name": "radio",
    "description": "🎶 Проигрывает музыку с радиостанций"
}


async def get_radio_stations():
    with open('./data/russian_radio_streams.json', 'r') as file:
        data_radio = json.load(file)
        return data_radio.items()


async def autocomplete(inter: disnake.CommandInteraction, query: str) -> list[OptionChoice]:
    radio = []

    stations = await get_radio_stations()
    filtered_stations = [(name, url) for name, url in stations if query.lower() in name.lower()]

    for name, url in filtered_stations[:25]:
        radio.append(disnake.OptionChoice(name=f"{name}", value=name))
    return radio


@commands.guild_only()
@commands.cooldown(5, 30, commands.BucketType.user)
async def command(
        inter: disnake.CommandInteraction,
        query: str = commands.Param(name="поиск",
                                    description="название радиостанции",
                                    autocomplete=autocomplete),
):
    await inter.response.defer()

    if inter.author.voice is not None:
        if not inter.guild.voice_client:
            channel = inter.author.voice.channel
            prem = channel.permissions_for(inter.me)
            if prem.connect and prem.speak and prem.view_channel:
                try:
                    player = await inter.user.voice.channel.connect(cls=Players, reconnect=True)
                except asyncio.TimeoutError:
                    return await inter.followup.send(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Попробуйте активировать команду снова!",
                            color=0xC31B21
                        ),
                        delete_after=10
                    )
            else:
                return await inter.followup.send(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="У меня нет доступа к каналу!",
                        color=0xC31B21
                    ),
                    delete_after=10
                )
        else:
            if inter.author.voice.channel != inter.guild.voice_client.channel:
                return await inter.followup.send(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description=f"Я уже нахожусь в канале {inter.guild.voice_client.channel.mention}",
                        color=0xC31B21
                    ),
                    delete_after=10
                )
            player = inter.guild.voice_client

        stations = await get_radio_stations()

        if query not in dict(stations):
            return await inter.send(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Вы выбрали отсутствующие радио",
                    color=0xC31B21
                ),
                delete_after=10
            )

        try:
            radio = await player.fetch_tracks(dict(stations).get(query))
        except mafic.TrackLoadException:
            return await inter.followup.send(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Радиостанция недоступна",
                    color=0xC31B21
                ),
                delete_after=10
            )

        if not radio:
            return await inter.followup.send(
                embed=disnake.Embed(
                    title=f"Радиостанция не найдена",
                    color=0xe74c3c
                ),
                delete_after=10
            )

        if player.current:
            player.queue.clear()
            try:
                await Players.destroy_player(self=None, player=player, bot=inter.bot, state=True)
            except mafic.errors.PlayerNotConnected:
                pass

        try:
            await player.play(radio[0], volume=50)
        except mafic.errors.PlayerNotConnected:
            return await inter.followup.send(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Плеер не был создан.\n"
                                "Заново подключите бота к голосовому каналу!",
                    color=0xC31B21
                ),
                delete_after=10
            )

        embed = disnake.Embed(
            description=f"**{query}**",
            color=disnake.Color.from_rgb(227, 182, 37)
        )
        embed.set_author(name="🔴 [LIVE] Играет радиостанция")
        embed.set_footer(text="Управление происходит только через команды")
        await inter.followup.send(
            embed=embed
        )
        player.controller_channel_id = inter.channel.id

    else:
        await inter.followup.send(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Вы не подключены к голосовому каналу!",
                color=0xC31B21
            ),
            delete_after=10
        )
