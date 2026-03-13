import json
import random
from typing import List, Dict

import disnake
import disnake.ext.commands as commands


config = {
    "name": "personage",
    "description": "✨ Угадай персонажа из аниме по кадру"
}


@commands.cooldown(3, 20, commands.BucketType.user)
async def command(
    inter: disnake.CommandInteraction
    ):
    view = GuessPersonageView(author=inter.author)
    await inter.response.send_message(embed=view.embed, view=view)
    view.message = await inter.original_message()


class GuessPersonageView(disnake.ui.View):
    def __init__(self, author: disnake.Member):
        self.author = author
        super().__init__(timeout=15.0)

        with open("data/personage.json", encoding="utf-8") as f:
            all_anime: List[Dict[str, str]] = json.load(f)
        
        five_anime = random.choices(all_anime, k=4)
        self.win_anime = random.choice(five_anime)
        self.dict_button = {}

        for anime in five_anime:
            _ = disnake.ui.Button(label=list(anime.keys())[0])
            _.callback=self.callback
            self.add_item(
                _
            )

            self.dict_button[_.custom_id] = _
        
        self.embed = disnake.Embed(
            color=0xd8833a,
            title="Угадай персонажа из аниме по кадру!"
        ).set_image(url=list(self.win_anime.items())[0][1])
        self.embed.set_footer(text="Время на ответ: 15 секунд")
    
    async def callback(self, interaction: disnake.Interaction):
        if interaction.user.id == self.author.id:
            self.timeout = None
            input_name_anime = self.dict_button[interaction.data.custom_id].label
            if list(self.win_anime.items())[0][0] == input_name_anime:
                self.embed.title = f"Правильно! Это {input_name_anime}"
                self.embed.color = 0x64b386
                self.embed.set_footer(text="")

            else:
                self.embed.title = f"Неправильно! Это {list(self.win_anime.items())[0][0]}"
                self.embed.color = 0xd65845
                self.embed.set_footer(text="")

            await interaction.response.edit_message(embed=self.embed, view=None)
        else:
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Команду активировал другой пользователь!",
                    color=0xC31B21
                ),
                ephemeral=True
            )

    async def on_timeout(self):
        self.embed.title = f"Время ожидания истекло! Это {list(self.win_anime.items())[0][0]}"
        self.embed.color = 0xd65845
        self.embed.set_footer(text="")
        await self.message.edit(embed=self.embed, view=None)