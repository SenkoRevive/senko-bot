import mafic
import disnake
from disnake.ext import commands

import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from mafic import Playlist

from settings.settings_music import Players, MusicButtons

load_dotenv()

config = {
    "name": "play",
    "description": "🎶 Проигрывает ваши любимые песни/плейлисты"
}

source = {
    "yandexmusic": ["254, 212, 43", "https://cdn.discordapp.com/emojis/1250082655022874777.png"],
    "spotify": ["30, 215, 96", "https://cdn.discordapp.com/emojis/1250084123054309486.png"],
    "soundcloud": ["255, 52, 18", "https://cdn.discordapp.com/emojis/1250084491574382656.png"],
    "bandcamp": ["35, 165, 180", "https://cdn.discordapp.com/emojis/1250084879656423574.png"],
}


async def autocomplete(inter: disnake.CommandInteraction, query: str, searchtype='scsearch') -> None:
    url = f"http://{os.environ['HOST_LAVALINK']}:{os.environ['PORT_LAVALINK']}/v4/loadtracks"
    params = {'identifier': f'{searchtype}:{query}'}
    headers = {
        'Authorization': os.environ['PASSWORD_LAVALINK'],
        'Accept': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            tracks = []
            if response.status == 200:
                data = await response.json()
                for item in data['data']:
                    tracks.append(
                        disnake.OptionChoice(name=f"{item['info']['title']}", value=item['info']['uri'][:100]))
            try:
                return tracks
            except disnake.errors.NotFound:
                pass


@commands.guild_only()
@commands.cooldown(5, 30, commands.BucketType.user)
async def command(
        inter: disnake.CommandInteraction,
        query: str = commands.Param(name="поиск",
                                    description="название или ссылка",
                                    autocomplete=autocomplete),
):
    await inter.response.defer()

    if inter.author.voice is not None:
        if not inter.guild.voice_client or not inter.guild.voice_client.channel:
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
            player = inter.guild.voice_client
            voice_client = inter.guild.voice_client

            if inter.author.voice.channel.id != inter.guild.voice_client.channel.id:
                if voice_client is None or not voice_client.is_connected():
                    await player.disconnect(force=True)
                    return await inter.followup.send(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Попробуйте активировать команду снова!",
                            color=0xC31B21
                        ),
                        delete_after=10
                    )
                else:
                    try:
                        channel = inter.guild.voice_client.channel.mention
                    except AttributeError:
                        await player.disconnect(force=True)
                        return await inter.followup.send(
                            embed=disnake.Embed(
                                title="Что-то пошло не так  👀",
                                description="Попробуйте активировать команду снова!",
                                color=0xC31B21
                            ),
                            delete_after=10
                        )

                    return await inter.followup.send(
                            embed=disnake.Embed(
                                title="Что-то пошло не так  👀",
                                description=f"Я уже нахожусь в канале {channel}",
                                color=0xC31B21
                            ),
                            delete_after=10
                        )

            if player.current:
                if player.current.stream:
                    return await inter.send(
                        embed=disnake.Embed(
                            title="Что-то пошло не так  👀",
                            description="Отключите радиостанцию, что бы выключать песни",
                            color=0xC31B21
                        ),
                        delete_after=10
                    )

        service_blacklist = ["twitch.tv", "music.yandex"]
        if any(service in query for service in service_blacklist) and inter.author.id != 679987861021655094:
            return await inter.followup.send(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Данная ссылка не поддерживается",
                    color=0xC31B21
                ),
                delete_after=10
            )

        try:
            tracks = await player.fetch_tracks(query)
        except mafic.TrackLoadException:
            return await inter.followup.send(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Песня/плейлист недоступен",
                    color=0xC31B21
                ),
                delete_after=10
            )

        if not tracks:
            return await inter.followup.send(
                embed=disnake.Embed(
                    title=f"Песня/плейлист не найдены",
                    color=0xe74c3c
                ),
                delete_after=10
            )

        if isinstance(tracks, Playlist):
            length = 0
            for track in tracks.tracks:
                player.queue.append(track)
                length += track.length

            embed = disnake.Embed(
                description=f"{tracks.name}",
                color=disnake.Color.from_rgb(254, 205, 42)
            )
            embed.add_field(name="Добавлено", value=f"`{len(tracks.tracks)}`", inline=True)
            embed.add_field(name="Длительность",
                            value=f"`{(length // 1000) // 60}:{(length // 1000) % 60}`", inline=True)
            embed.set_author(name="Плейлист добавлен в очередь",
                             icon_url="https://cdn.discordapp.com/emojis/1250133741289083013.png")
            await inter.followup.send(
                embed=embed
            )

            if not player.current:
                await player.play(player.queue.pop(0), volume=player.volume)

        else:
            track = tracks[0]
            source_info = source.get(track.source, ["227, 182, 37", ""])
            rgb_string, icon_url = source_info
            r, g, b = map(int, rgb_string.split(", "))

            if track.source == "youtube":
                embed = disnake.Embed(
                    description=f"{track.title}",
                    color=disnake.Color.from_rgb(r, g, b)
                )
                embed.add_field(name="Автор", value=track.author, inline=True)
                embed.add_field(name="Длительность",
                                value=f"`{(track.length // 1000) // 60}:{(track.length // 1000) % 60}`", inline=True)
                embed.set_author(name="Добавлено в очередь", icon_url="https://cdn.discordapp.com/emojis/1250133741289083013.png")
                await inter.followup.send(
                    embed=embed
                )
            else:
                embed = disnake.Embed(
                    description=f"[{track.title}]({track.uri})",
                    color=disnake.Color.from_rgb(r, g, b)
                )
                embed.add_field(name="Автор", value=track.author, inline=True)
                embed.add_field(name="Длительность",
                                value=f"`{(track.length // 1000) // 60}:{(track.length // 1000) % 60}`", inline=True)
                embed.set_author(name="Добавлено в очередь", icon_url=icon_url)
                embed.set_thumbnail(url=track.artwork_url)
                await inter.followup.send(
                    embed=embed
                )

            if player.current:
                player.queue.append(track)
            else:
                try:
                    await player.play(track, volume=player.volume)
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

        if player.controller_id == 0 or not player.current:
            prem = inter.channel.permissions_for(inter.me)
            embed_error = disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Не удалось отправить звуковую панель в канал (нет доступа)\n"
                            "**Доступно управление только через команды!**",
                color=0xC31B21
            )

            if prem.view_channel and prem.send_messages:
                try:
                    player.controller = await inter.channel.send(
                        embed=await Players.playerMessage(self=None, player=player),
                        view=MusicButtons(player=player, bot=inter.bot)
                    )
                    player.controller_id = player.controller.id
                    player.controller_channel_id = player.controller.channel.id
                except disnake.errors.Forbidden:
                    await inter.send(embed=embed_error, ephemeral=True)
            else:
                await inter.send(embed=embed_error, ephemeral=True)

    else:
        await inter.followup.send(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Вы не подключены к голосовому каналу!",
                color=0xC31B21
            ),
            delete_after=10
        )
