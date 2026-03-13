import disnake
from disnake.ext import commands
from mafic import TrackEndEvent

from settings.settings_music import Players, MusicButtons


class MusicEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def info_leave_message(self, channel):
        if channel:
            embed = disnake.Embed(
                description=f"**Из голосового канала вышли все пользователи**",
                color=disnake.Color.from_rgb(254, 205, 42)
            )
            embed.set_author(name="Выход из голосового канала",
                             icon_url="https://cdn.discordapp.com/emojis/1250133741289083013.png")
            await channel.send(embed=embed)

    async def player_controller(self, channel, player):
        if channel is not None:
            player.controller = await channel.send(
                embed=await Players.playerMessage(self=None, player=player),
                view=MusicButtons(player=player, bot=self.bot)
            )
            player.controller_id = player.controller.id

    @commands.Cog.listener()
    async def on_track_end(self, event: TrackEndEvent[Players]):
        player = event.player
        msg = self.bot.get_message(int(player.controller_id))
        channel = self.bot.get_channel(int(player.controller_channel_id))

        if msg is not None:
            await msg.delete()

        if player.loop is True:
            await player.play(event.track, start_time=0)
            await self.player_controller(channel=channel, player=player)
            return

        if player.queue:
            await player.play(player.queue.pop(0))
            await self.player_controller(channel=channel, player=player)
            return

        else:
            await Players.destroy_player(self=self, player=player, bot=self.bot, state=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = member.guild.voice_client

        if not player:
            return

        channel = self.bot.get_channel(int(player.controller_channel_id))

        if not any(not member.bot for member in player.channel.members):
            await self.info_leave_message(channel)
            await Players.destroy_player(self=self, player=player, bot=self.bot, state=False)

        elif member.id == self.bot.user.id and after.channel is None:
            await self.info_leave_message(channel)
            await Players.destroy_player(self=self, player=player, bot=self.bot, state=False)


def setup(bot):
    bot.add_cog(MusicEvents(bot))
