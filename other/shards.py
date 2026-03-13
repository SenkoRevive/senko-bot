import disnake
from disnake.ext import commands


config = {
    "name": "shards",
    "description": "⚙️ Информация о шардах"
}


@commands.cooldown(5, 30, commands.BucketType.user)
async def command(inter: disnake.CommandInteraction):
    shards = []
    shards.append(f"<a:Dance:1113484035927314482> Информация о шардах:")
    for i in range(inter.bot.shard_count):
        shard = inter.bot.get_shard(i)
        status = 'работает' if shard.is_closed() == False else 'не работает'
        mes = f"- #{i}: Активность: {status}, Пинг: {round(shard.latency * 1000)} ms, Кол. серверов: {len([guild for guild in inter.bot.guilds if guild.shard_id == shard.id])}"
        shards.append(f"{mes}")
    await inter.response.send_message("\n".join(shards))