import json
import disnake
from disnake.ext import commands


async def check_admin(inter):
    if inter.author.id == 679987861021655094:
        return True
    else:
        await inter.send("❌ Access denied")
        return False


class AdminCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[1064586888989642843])
    async def admin(self, inter):
        await inter.response.defer(ephemeral=True)

    @admin.sub_command(description="⚙️ Get bot.log", guild_ids=[1064586888989642843])
    async def logs(self, inter, file: str = commands.Param(name="file", choices=["bot.log", "spring.log"])):
        if await check_admin(inter):
            if file == "bot.log":
                await inter.send(file=disnake.File(f"./data/bot.log"), ephemeral=True)
            elif file == "spring.log":
                await inter.send(file=disnake.File(f"./data/logs/spring.log"), ephemeral=True)

    @admin.sub_command(description="⚙️ Get server info", guild_ids=[1064586888989642843])
    async def server(self, inter, server: str = commands.Param(name="id-server")):
        if await check_admin(inter):
            guild = self.bot.get_guild(int(server))

            if guild is None:
                return await inter.send("❌ Not Found")

            with open("data/permission.json", encoding="utf-8") as f:
                permission = json.load(f)

            emb = disnake.Embed(title=f"{guild.name} | `{guild.id}` | #{guild.shard_id}", color=0xF1C40F)
            emb.add_field(name="**<:Info:1064590530153037944> Информация:**",
                          value=f"**Владелец:** @{guild.owner.name} (ID: {guild.owner.id}) \n"
                                f"**Дата создания:** {guild.created_at.strftime('%d.%m.%Y')} \n"
                                f"**Количество ботов:** {len(([member for member in guild.members if member.bot])) - 1} \n"
                                f"**Количество людей:** {guild.member_count - len(([member for member in guild.members if member.bot]))} \n\n"
                                f"**Разрешения бота:**\n{'Администратор' if guild.me.guild_permissions.administrator else ', '.join([permission[str(p[0]).replace('_', ' ').title()] for p in guild.me.guild_permissions if p[1]])}",
                          inline=False
                          )
            if guild.icon != None:
                emb.set_thumbnail(url=str(guild.icon.url))
            await inter.send(embed=emb)


def setup(bot):
    bot.add_cog(AdminCommand(bot))
