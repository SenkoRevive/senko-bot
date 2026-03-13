import disnake
from disnake.abc import Connectable
from disnake.ext import commands

import os
from mafic import NodePool, Track, Player
from dotenv import load_dotenv
from random import shuffle

from music.playlist import PlaylistView


load_dotenv()


class Setup(commands.AutoShardedInteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pool = NodePool(self)
        self.loop.create_task(self.add_nodes())

    async def add_nodes(self):
        await self.pool.create_node(
            host=os.environ['HOST_LAVALINK'],
            port=int(os.environ['PORT_LAVALINK']),
            label="MAIN",
            password=os.environ["PASSWORD_LAVALINK"],
        )


class MusicButtons(disnake.ui.View):
    def __init__(self, player, bot):
        super().__init__(timeout=None)
        self.player = player
        self.bot = bot

    async def check(self, inter):
        if not inter.user.voice:
            await inter.response.send_message(
                embed=disnake.Embed(
                    title=f"Вы должны находиться в голосовом канале с ботом для управление музыкой",
                    color=0xC31B21
                ), ephemeral=True, delete_after=10)
            return False

        return True

    @disnake.ui.button(emoji="⏮️", style=disnake.ButtonStyle.gray)
    async def back(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if await self.check(interaction):
            await self.player.seek(0)
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title=f"⏮️  Перемотка к началу текущего трека",
                    color=disnake.Color.from_rgb(227, 182, 37)
                ), ephemeral=True, delete_after=5)

            if self.player.paused:
                await self.player.resume()

    @disnake.ui.button(emoji="⏯️", style=disnake.ButtonStyle.gray)
    async def pause_resume(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if await self.check(interaction):
            if not self.player.paused:
                await self.player.pause()
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"⏸️  Пауза",
                        color=disnake.Color.from_rgb(227, 182, 37)
                    ), ephemeral=True, delete_after=5)
            else:
                await self.player.resume()
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"▶️  Воспроизведение",
                        color=disnake.Color.from_rgb(227, 182, 37)
                    ), ephemeral=True, delete_after=5)

    @disnake.ui.button(emoji="⏭️", style=disnake.ButtonStyle.gray)
    async def skip(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if await self.check(interaction):
            if len(self.player.queue) >= 1:
                await self.player.stop()
            else:
                await Players.destroy_player(self=self, player=self.player, bot=self.bot, state=True)

            await interaction.response.send_message(
                embed=disnake.Embed(
                    title=f"⏭️  Пропуск трека",
                    color=disnake.Color.from_rgb(227, 182, 37)
                ), ephemeral=True, delete_after=5)

    @disnake.ui.button(emoji="⏹️", style=disnake.ButtonStyle.gray)
    async def stop(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if await self.check(interaction):
            await Players.destroy_player(self=self, player=self.player, bot=self.bot, state=False)
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title=f"⏹️  Воспроизведение остановлено",
                    color=disnake.Color.from_rgb(227, 182, 37)
                ), ephemeral=True)

    @disnake.ui.button(emoji="📄", style=disnake.ButtonStyle.gray)
    async def playlist(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if await self.check(interaction):
            if len(self.player.queue) >= 1:
                playlist = '\n'.join([f"{idx + 1}. {track.author} - {track.title} (`{(track.length // 1000) // 60}:{(track.length // 1000) % 60}`)" for idx, track in enumerate(self.player.queue[0:10])])
                if len(self.player.queue) > 10:
                    await interaction.response.send_message(f"📄 Текущий плейлист (Страница 1):\n\n{playlist}",
                                                            ephemeral=True,
                                                            view=PlaylistView(self.player, interaction))
                else:
                    await interaction.response.send_message(f"📄 Текущий плейлист:\n\n{playlist}",
                                                                 ephemeral=True)
            else:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"📄  Плейлист пустой",
                        color=disnake.Color.from_rgb(227, 182, 37)
                    ), ephemeral=True, delete_after=5)

    @disnake.ui.button(emoji="🔁", style=disnake.ButtonStyle.gray)
    async def repeat(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if await self.check(interaction):
            if self.player.loop is False:
                self.player.loop = True
                await interaction.response.send_message(
                        embed=disnake.Embed(
                            title=f"🔁  Включен режим повтора для текущего трека",
                            color=disnake.Color.from_rgb(227, 182, 37)
                        ), ephemeral=True, delete_after=5)
            else:
                self.player.loop = False
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"🔁  Выключен режим повтора",
                        color=disnake.Color.from_rgb(227, 182, 37)
                    ), ephemeral=True, delete_after=5)

    @disnake.ui.button(emoji="🔀", style=disnake.ButtonStyle.gray)
    async def shuffle(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if await self.check(interaction):
            if len(self.player.queue) >= 3:
                shuffle(self.player.queue)
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"🔀  Плейлист был перемешан",
                        color=disnake.Color.from_rgb(227, 182, 37)
                    ), ephemeral=True, delete_after=5)
            else:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"🔀  В плейлисте меньше 3-х треков",
                        color=0xC31B21
                    ), ephemeral=True, delete_after=5)

    @disnake.ui.button(emoji="🔉", style=disnake.ButtonStyle.gray)
    async def volume_decrease(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if await self.check(interaction):
            if self.player.volume >= 0:
                self.player.volume -= 10
                await self.player.set_volume(self.player.volume)
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"🔉  Громкость уменьшена на 10%",
                        color=disnake.Color.from_rgb(227, 182, 37)
                    ), ephemeral=True, delete_after=5)
            else:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"🔉  Громкость уже на 0%",
                        color=0xC31B21
                    ), ephemeral=True, delete_after=5)

    @disnake.ui.button(emoji="🔊", style=disnake.ButtonStyle.gray)
    async def volume_add(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if await self.check(interaction):
            if self.player.volume <= 200:
                self.player.volume += 10
                await self.player.set_volume(self.player.volume)
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"🔉  Громкость прибавлена на 10%",
                        color=disnake.Color.from_rgb(227, 182, 37)
                    ), ephemeral=True, delete_after=5)
            else:
                await interaction.response.send_message(
                    embed=disnake.Embed(
                        title=f"🔉  Громкость уже на 200%",
                        color=0xC31B21
                    ), ephemeral=True, delete_after=5)


class Players(Player[Setup]):
    def __init__(self, client: Setup, channel: Connectable) -> None:
        super().__init__(client, channel)

        self.loop: bool = False
        self.queue: list[Track] = []
        self.volume: int = 50
        self.controller_id: int = 0
        self.controller_channel_id: int = 0

    async def playerMessage(self, player):
        track = player.current

        if track.source == "youtube":
            embed = disnake.Embed(
                description=f"{track.title}",
                color=disnake.Color.from_rgb(227, 182, 37)
            )
            embed.add_field(name="Автор", value=track.author, inline=True)
            embed.add_field(name="Длительность",
                            value=f"`{(track.length // 1000) // 60}:{(track.length // 1000) % 60}`", inline=True)
            embed.set_author(name="Сейчас играет", icon_url="https://cdn.discordapp.com/emojis/1250133741289083013.png")
        else:
            embed = disnake.Embed(
                description=f"[{track.title}]({track.uri})",
                color=disnake.Color.from_rgb(227, 182, 37)
            )
            embed.add_field(name="Автор", value=track.author, inline=True)
            embed.add_field(name="Длительность",
                            value=f"`{(track.length // 1000) // 60}:{(track.length // 1000) % 60}`", inline=True)
            embed.set_author(name="Сейчас играет", icon_url="https://cdn.discordapp.com/emojis/1250133741289083013.png")
            embed.set_thumbnail(url=track.artwork_url)

        return embed

    async def destroy_player(self, player, bot, state: False):
        if player.controller_id != 0:
            msg = bot.get_message(int(player.controller_id))
            if msg:
                await msg.delete()

        if state:
            player.controller_id = 0
            player.controller = 0
            await player.stop()
            return

        await player.disconnect()
