import disnake
from disnake.ext import commands


class View(disnake.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

        self.add_item(
            disnake.ui.Button(style=disnake.ButtonStyle.url, label="Сервер поддержки", url="https://senko-bot.com/support")
        )


class NewGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        embed = disnake.Embed(
            title="<a:SenkoTail:1029788770570088548>  Спасибо за приглашение",
            description=(
                "Сэнко — это милая лисичка, которая поможет вам изгнать тьму с вашего сервера и поднять настроение <a:SenkoBliss:1068571979046727780>\n"
                f"Спасибо, что выбрали и добавили на сервер **{guild.name}**!"
                "\n### Рекомендуемые команды:\n"
                "- </play:1261637398555529316>\n"
                "- </radio:1262382474269298699>\n"
                "- </anime:1240271012990554146>\n"
                "- </personage:1240271012990554147>\n"
                "- </welcome-settings:1000453634326274101>\n"
            ),
            color=0xe67e22
        )
        embed.set_footer(text="Некоторые команды не работают в личных сообщениях!")

        try:
            integrations = await guild.integrations()
            for integration in integrations:
                if integration.account.id == str(self.bot.user.id):
                    member = guild.get_member(integration.user.id)
                    await member.send(
                        embed=embed, view=View()
                    )
        except:
            pass


def setup(bot):
    bot.add_cog(NewGuild(bot))
