import os
import discord
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
# Conectar a MongoDB
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
warns_collection = db["image_warns"]
violence_collection = db["violent_images"]

class WarnsCommand(commands.Cog):
    """Cog para el comando /warns"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="warns", description="Mostrar el número de warns de NSFW de un usuario")
    @app_commands.describe(
        user="El usuario al que quieres consultar warns de NSFW"
    )
    async def warns(self, interaction: discord.Interaction, user: discord.Member):
        # Obtener warns de NSFW
        nsfw_data = warns_collection.find_one({
            "guild_id": interaction.guild.id,
            "user_id": user.id
        })
        nsfw_warns = nsfw_data.get("warns", 0) if nsfw_data else 0

        embed = discord.Embed(
            title="📊 Warns de NSFW",
            color=discord.Color.blue()
        )
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        embed.add_field(name="⚠️ Warns acumulados", value=str(nsfw_warns), inline=True)
        embed.set_footer(text=f"Solicitado por {interaction.user}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(WarnsCommand(bot))