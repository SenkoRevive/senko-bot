import disnake
import disnake.ext.commands as commands

import json
from random import randint, choice

config = {
    "name": "country",
    "description": "✨ Угадай страну по флагу"
}


@commands.cooldown(3, 30, commands.BucketType.user)
async def command(
        inter: disnake.CommandInteraction
):
    await inter.response.defer()

    with open('data/country.json', 'r', encoding='utf-8') as file:
        root = json.load(file)

    view = GuessCountryView(author=inter.author, root=root)
    await inter.followup.send(embed=view.embed, view=view)
    view.message = await inter.original_message()


class GuessCountryView(disnake.ui.View):
    def __init__(self, author: disnake.Member, root):
        self.author = author
        super().__init__(timeout=15.0)

        country_array = []
        self.dict_button = {}

        for i in range(4):
            rand = randint(0, 197)
            country_array.append({root[rand]["name"]: root[rand]['flags']})
            self.win_country = choice(country_array)

        for anime in country_array:
            _ = disnake.ui.Button(label=list(anime.keys())[0])
            _.callback = self.callback
            self.add_item(
                _
            )
            self.dict_button[_.custom_id] = _

        self.embed = disnake.Embed(
            color=0xd8833a,
            title="Угадай страну по флагу!"
        ).set_image(url=list(self.win_country.values())[0])
        self.embed.set_footer(text="Время на ответ: 15 секунд")

    async def callback(self, interaction: disnake.Interaction):
        if interaction.user.id == self.author.id:
            self.timeout = None
            input_name_anime = self.dict_button[interaction.data.custom_id].label
            if list(self.win_country.items())[0][0] == input_name_anime:
                self.embed.title = f"Правильно! Это {input_name_anime}"
                self.embed.color = 0x64b386
                self.embed.set_footer(text="")

            else:
                self.embed.title = f"Неправильно! Это {list(self.win_country.items())[0][0]}"
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
        self.embed.title = f"Время ожидания истекло! Это {list(self.win_country.items())[0][0]}"
        self.embed.color = 0xd65845
        self.embed.set_footer(text="")
        await self.message.edit(embed=self.embed, view=None)