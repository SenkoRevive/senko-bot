import disnake
import disnake.ext.commands as commands


config = {
    "name": "help",
    "description": "⚙️ Список всех доступных команд"
}


class HelpSend(disnake.ui.StringSelect):
    def __init__(self, inter):
        self.inter = inter
        options = [
            disnake.SelectOption(label="Главная страница", emoji="🏠"),
            disnake.SelectOption(label="Модерация", description="Изгоним тьму из твоей души!",
                                 emoji="🛡"),
            disnake.SelectOption(label="Утилиты", description="Братик, как пользоваться рисоваркой?",
                                 emoji="🛠"),
            disnake.SelectOption(label="Музыка", description="Давай потанцуем, братик!",
                                 emoji="🎶"),
            disnake.SelectOption(label="Развлечение", description="Давай поиграем в приставку?",
                                 emoji="✨"),
            disnake.SelectOption(label="РП", description="* Сэнко поздоровалась со всеми *",
                                 emoji="🎭"),
            disnake.SelectOption(label="NSFW", description="Не трогай меня за хвост и уши",
                                 emoji="🔞"),
            disnake.SelectOption(label="Ссылки проекта", emoji="🔗"),
            disnake.SelectOption(label="Другое", emoji="⚙️")
        ]

        super().__init__(
            placeholder="Выберите категорию",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        if inter.user.id != self.inter.user.id:
            return await inter.response.send_message(
                embed=disnake.Embed(
                    title="Что-то пошло не так  👀",
                    description="Команду активировал другой пользователь!",
                    color=0xC31B21
                ),
                ephemeral=True
            )

        if inter.values[0] == "Главная страница":
            emb = disnake.Embed(
                title='🏠  Главная страница', description=
                f'Для просмотра команд, выберите категорию \n\n'
                f'Версия бота от [**13.07.2024**](https://docs.senko-bot.com/obnovleniya/13.07.2024)',
                color=0xfff700)
            emb.set_thumbnail(url=inter.me.avatar.url)
            await inter.response.edit_message(embed=emb)
        elif inter.values[0] == "Ссылки проекта":
            emb = disnake.Embed(
                title="🔗  Ссылки проекта", description=
                      f'\n [**Cсылка на сайт**](https://senko-bot.com/) \
                      \n [**Ссылка на документацию**](https://docs.senko-bot.com/) \
                      \n [**Ссылка на boosty.to**](https://boosty.to/senko-bot) \
                      \n [**Cсылка на сервер поддержки**](https://senko-bot.com/support) \n',
                color=0x979c9f)
            await inter.response.edit_message(embed=emb)
        elif inter.values[0] == "Модерация":
            emb = disnake.Embed(
                title="🛡  Модерация", description=
                      f'\n **/ban** - заблокировать пользователя \
                      \n **/kick** - выгнать пользователя \
                      \n **/mute** - мьют пользователя \
                      \n **/unban** - разблокировать пользователя \
                      \n **/unmute** - размьют пользователя \
                      \n **/clear** - очистка чата \
                      \n **/slowmode** - добавить медленный режим \n',
                color=0x3498db)
            await inter.response.edit_message(embed=emb)
        elif inter.values[0] == "Утилиты":
            emb = disnake.Embed(
                title="🛠  Утилиты", description=
                      f'\n **/welcome-settings** - настройка приветствий пользователей \
                      \n **/logging** - настройка журнала действий \
                      \n **/auto-role** - настройка авто ролей \
                      \n **/server** - информация о сервере \
                      \n **/user** - информация о пользователе \
                      \n **/avatar** - вывод аватара пользователя \
                      \n **/banner** - вывод баннера пользователя \
                      \n **/get-emoji** - преобразование эмодзи в картинку \n',
                color=0xf1c40f)
            await inter.response.edit_message(embed=emb)
        elif inter.values[0] == "Музыка":
            emb = disnake.Embed(
                title="🎶  Музыка", description=
                    f'\n **/play** - проигрывает ваши любимые песни/плейлисты \
                      \n **/radio** - проигрывает музыку с радиостанций \
                      \n **/pause** - приостановка проигрывания трека \
                      \n **/resume** - воспроизведение проигрывания трека \
                      \n **/stop** - полная остановка проигрывания \
                      \n **/skip** - пропуск трека(-ов) \
                      \n **/loop** - настройка режима повтора \
                      \n **/volume** - настройка громкости треков \
                      \n **/playlist** - список треков в очереди \
                      \n **/shuffle** - перемешивание треков в плейлисте \n',
                color=disnake.Color.from_rgb(227, 182, 37))
            await inter.response.edit_message(embed=emb)
        elif inter.values[0] == "Развлечение":
            emb = disnake.Embed(
                title="✨  Развлечение", description=
                      f'\n **/personage** - угадай персонажа из аниме по кадру \
                      \n **/anime** - угадай аниме по кадру \
                      \n **/country** - угадай страну по флагу \
                      \n **/senko** - посмотри на мои фотографии \
                      \n **/shiro** - посмотри на фотографии Широ \
                      \n **/fox** - просмотр фотографий лисиц \n',
                color=0xe67e22)
            await inter.response.edit_message(embed=emb)
        elif inter.values[0] == "РП":
            emb = disnake.Embed(
                title="🎭  РП", description=
                      f'\n **/rp** - выразите свою эмоцию необычным способом \n',
                color=disnake.Color.from_rgb(195, 174, 229))
            await inter.response.edit_message(embed=emb)
        elif inter.values[0] == "NSFW":
            if not inter.channel.nsfw:
                await inter.response.send_message(
                    embed=disnake.Embed(
                        title="Что-то пошло не так  👀",
                        description="Этот раздел можно открыть только в NSFW канале!",
                        color=0xC31B21
                    ),
                    view=disnake.ui.View().add_item(
                        disnake.ui.Button(
                            label="Как настроить?",
                            url="https://support.discord.com/hc/ru/articles/115000084051#h_adc93a2c-8fc3-4775-be02-bbdbfcde5010"
                        )
                    ),
                    ephemeral=True
                )
            else:
                emb = disnake.Embed(
                    title="🔞  NSFW", description=
                    f'\n **/nsfw** - 18+ \n',
                    color=0x9b59b6)
                await inter.response.edit_message(embed=emb)
        elif inter.values[0] == "Другое":
            emb = disnake.Embed(
                title="⚙️  Другое", description=
                      f'\n **/help** - список всех доступных команд \
                      \n **/shards** - информация о шардах \
                      \n **/bot** - информация о Сэнко \n',
                color=0x979c9f)
            await inter.response.edit_message(embed=emb)


class DropDownView(disnake.ui.View):
    def __init__(self, inter):
        self.inter = inter
        super().__init__(timeout=90.0)
        self.add_item(HelpSend(inter))

    async def on_timeout(self):
        msg = await self.inter.original_response()
        await msg.edit(view=None)


@commands.cooldown(5, 30, commands.BucketType.user)
async def command(inter: disnake.CommandInteraction):
    emb = disnake.Embed(
        title='🏠  Главная страница', description=
        f'Для просмотра команд, выберите категорию \n\n'
        f'Версия бота от [**13.07.2024**](https://docs.senko-bot.com/obnovleniya/13.07.2024)',
        color=0xfff700)
    emb.set_thumbnail(url=inter.me.avatar.url)
    await inter.response.send_message(embed=emb, view=DropDownView(inter))