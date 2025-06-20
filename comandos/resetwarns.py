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

class ResetWarnsCommand(commands.Cog):
    """Cog para el comando /resetwarns"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="resetwarns", description="Reiniciar los warns de NSFW de un usuario")
    @app_commands.describe(
        user="El usuario al que deseas reiniciar los warns"
    )
    async def resetwarns(self, interaction: discord.Interaction, user: discord.Member):
        # Resetear warns de NSFW
        warns_collection.update_one(
            {"guild_id": interaction.guild.id, "user_id": user.id},
            {"$set": {"warns": 0}},
            upsert=True
        )

        await interaction.response.send_message(
            f"✅ Los warns de {user.mention} han sido restablecidos a 0.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ResetWarnsCommand(bot))