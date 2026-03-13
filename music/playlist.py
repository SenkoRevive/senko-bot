import disnake
from disnake.ext import commands
from disnake.ui import View, Button


config = {
    "name": "playlist",
    "description": "🎶 Список треков в очереди"
}


class PlaylistView(View):
    def __init__(self, player, inter, page=0):
        super().__init__(timeout=60)
        self.TRACKS_PER_PAGE = 10
        self.player = player
        self.inter = inter
        self.page = page

        self.previous_button = Button(emoji="◀️", style=disnake.ButtonStyle.gray, custom_id="previous")
        self.next_button = Button(emoji="▶️", style=disnake.ButtonStyle.gray, custom_id="next")

        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        self.previous_button.disabled = True
        self.next_button.disabled = False

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

        self.update_buttons()

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.inter.edit_original_message(view=self)

    async def previous_page(self, interaction: disnake.MessageInteraction):
        self.page -= 1
        await self.update_buttons()
        await self.update(interaction)

    async def next_page(self, interaction: disnake.MessageInteraction):
        self.page += 1
        await self.update_buttons()
        await self.update(interaction)

    async def update(self, interaction: disnake.MessageInteraction):
        start = self.page * self.TRACKS_PER_PAGE
        end = start + self.TRACKS_PER_PAGE
        playlist = '\n'.join(
            [f"{(idx + 1) + (self.page * 10)}. {track.author} - {track.title} (`{(track.length // 1000) // 60}:{(track.length // 1000) % 60}`)"
             for idx, track in enumerate(self.player.queue[start:end])])
        await interaction.response.edit_message(content=f"📄 Текущий плейлист (Страница {self.page + 1}):\n\n{playlist}", view=self)

    async def update_buttons(self):
        page = self.page

        if page <= 0:
            self.previous_button.disabled = True
            self.next_button.disabled = False
            return
        if page != 0 and page != (len(self.player.queue) // self.TRACKS_PER_PAGE):
            self.previous_button.disabled = False
            self.next_button.disabled = False
            return
        if page >= (len(self.player.queue) // self.TRACKS_PER_PAGE):
            self.previous_button.disabled = False
            self.next_button.disabled = True
            return


@commands.guild_only()
@commands.cooldown(5, 30, commands.BucketType.user)
async def command(inter: disnake.CommandInteraction):
    await inter.response.defer(ephemeral=True)
    player = inter.guild.voice_client

    if not player:
        return await inter.followup.send(
            embed=disnake.Embed(
                title="Что-то пошло не так  👀",
                description="Музыка сейчас не проигрывается",
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
                description="Вы должны находиться в голосовом канале с ботом для управления музыкой",
                color=0xC31B21
            )
        )

    if len(player.queue) >= 1:
        playlist = '\n'.join(
            [f"{idx + 1}. {track.author} - {track.title} (`{(track.length // 1000) // 60}:{(track.length // 1000) % 60}`)"
             for idx, track in enumerate(player.queue[0:10])])
        if len(player.queue) > 10:
            await inter.send(f"📄 Текущий плейлист (Страница 1):\n\n{playlist}", ephemeral=True,
                             view=PlaylistView(player, inter))
        else:
            await inter.send(f"📄 Текущий плейлист:\n\n{playlist}", ephemeral=True)
    else:
        await inter.send(
            embed=disnake.Embed(
                title="📄 Плейлист пустой",
                color=disnake.Color.from_rgb(227, 182, 37)
            ), ephemeral=True)
