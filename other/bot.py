import disnake
import disnake.ext.commands as commands
from disnake.utils import format_dt
from settings.settings_db import SettingsDataBase

config = {
    "name": "bot",
    "description": "⚙️ Информация о Сэнко"
}


@commands.guild_only()
@commands.cooldown(5, 30, commands.BucketType.user)
async def command(inter: disnake.CommandInteraction):
    node = inter.bot.pool.nodes[0]
    stats = node.stats

    emb = disnake.Embed(title="<a:SenkoTail:1029788770570088548>  Информация обо мне:",
                        description="**Разработчик:** <@679987861021655094> (@dudosa) \n"
                                    f"Ваш сервер расположен на **#{inter.guild.shard_id}** шарде"
                        , color=0xe67e22)
    emb.add_field(name="**<:Info:1064590530153037944> Основная статистика:**",
                  value=f"**Пинг бота:** {round(inter.bot.latency * 1000)} ms \n"
                        f"**Пинг базы данных:** {await SettingsDataBase.db_ping(self=None, bot=inter.bot)} ms \n"
                        f"**Количество серверов:** {len(inter.bot.guilds)} \n"
                        f"**Количество участников:** {len(inter.bot.users)} \n"
                        f"**Время работы:** {format_dt(inter.bot.start_time, style='R')} \n"
                        f"**Дата создание:** <t:1644950395:f> \n",
                  inline=False
                  )
    emb.add_field(name="**🎶  Музыкальная статистика:**",
                  value=f"**Исп. оперативной память:** {stats.memory.used / 1024 / 1024:.0f} MiB\n"
                        f"**Исп. процессора:** {stats.cpu.lavalink_load * 100:.2f}% \n"
                        f"**Кол. слушателей:** {stats.player_count}\n"
                        f"**Кол. нодов:** {len(inter.bot.pool.nodes)}",
                  inline=False
                  )
    await inter.response.send_message(embed=emb)
