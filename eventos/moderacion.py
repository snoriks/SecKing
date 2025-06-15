import discord
from discord.ext import commands
import openai
import os

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        try:
            response = openai.Moderation.create(input=message.content)
            result = response["results"][0]

            if result["flagged"]:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, tu mensaje fue eliminado por violar las reglas del servidor.")
                print(f"[MODERACIÓN] Mensaje eliminado: {message.content}")
        except Exception as e:
            print(f"[ERROR OpenAI] {e}")

        await self.bot.process_commands(message)

# Versión moderna (requerida para load_extension async)
async def setup(bot):
    await bot.add_cog(Moderacion(bot))
