from disnake.ext import commands


class AutoRolesEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        idServer = member.guild.id
        query = f"""SELECT id_roles FROM autorole_settings WHERE id_server={idServer}"""
        res = await self.bot.cursor.fetchval(query)

        if res is not None:
            guild = self.bot.get_guild(idServer)
            for roles in res:
                role = guild.get_role(roles)
                if role is not None and member.guild.me.guild_permissions.manage_roles:
                    await member.add_roles(role, reason="Выдана системой авто ролей")

def setup(bot):
    bot.add_cog(AutoRolesEvent(bot))