import json

import disnake
from disnake.ext import commands

import os
import PIL
import numpy
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps, ImageFont, ImageSequence


class WelcomeEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        query = f"""SELECT content FROM welcome_settings WHERE id_server={member.guild.id}"""
        res = await self.bot.cursor.fetchval(query)

        if res is None or member.bot == True:
            pass
        else:
            data = json.loads(res)
            image = Image.open("./data/file.png")
            img = image.resize((1870, 1034)).convert("RGBA")
            idraw = ImageDraw.Draw(img)
            title = ImageFont.truetype('./data/DelaGothicOne-Regular.ttf', size=80)
            idraw.text((715, 640), f"@{member.name}", font=title, fill="black", anchor="mm")

            avatar = member.display_avatar.with_size(512)
            avt = BytesIO(await avatar.read())
            imga = Image.open(avt).convert("RGBA")
            pfp = imga.resize((420, 420))
            mask = Image.open('./data/mask.png').convert('L').resize((420, 420))

            if isinstance(pfp, PIL.GifImagePlugin.GifImageFile):
                pfp = Image.fromarray(numpy.asarray(ImageSequence.Iterator(pfp)[1])).resize((420, 420)).convert("RGBA")

            pfp = ImageOps.fit(pfp, mask.size, centering=(0.5, 0.5))
            pfp.putalpha(mask)

            img.alpha_composite(pfp, (515, 97))
            img.save(f"./data/profile_{member.id}.png")

            embed = disnake.Embed(title=f'{data[0]["title"]}, @{member.name}!', description=data[0]["description"], color=0xe67e22)
            file = disnake.File(f"./data/profile_{member.id}.png", filename="image.png")
            embed.set_image(url="attachment://image.png")
            embed.set_footer(text=f"Участник под номером #{member.guild.member_count}")

            method_send = await self.bot.cursor.fetchval(f"""SELECT method_send FROM welcome_settings WHERE id_server={member.guild.id}""")

            if method_send == ".":
                dm = await member.create_dm()
                await dm.send(content=member.mention, file=file, embed=embed, components=[
                    disnake.ui.Button(label=f"Отправлено с {member.guild.name}", emoji="📨", disabled=True)
                ])
            else:
                try:
                    async with aiohttp.ClientSession() as webhook:
                        webhook = disnake.Webhook.from_url(url=method_send, session=webhook)
                        await webhook.send(content=member.mention, file=file, embed=embed)
                except:
                    async with self.bot.cursor.acquire() as connection:
                        tr = connection.transaction()
                        await tr.start()
                        try:
                            await self.bot.cursor.execute(
                                f"""DELETE FROM logging_settings WHERE id_server={member.guild.id}""",
                            )
                        except:
                            await tr.rollback()
                            raise
                        else:
                            await tr.commit()

            os.remove(f"./data/profile_{member.id}.png")

def setup(bot):
    bot.add_cog(WelcomeEvent(bot))