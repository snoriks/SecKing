import os
import discord
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
manual_warns = db["manual_warns"]
nsfw_warns = db["image_warns"]
violent_warns = db["violent_images"]

class WarnsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="warns", description="Ver los warns acumulados de un usuario")
    @app_commands.describe(user="El usuario al que quieres consultar los warns")
    async def warns(self, interaction: discord.Interaction, user: discord.Member):
        guild_id = interaction.guild.id

        # Buscar warns manuales
        manual_data = manual_warns.find_one({"guild_id": guild_id, "user_id": user.id})
        manual_reasons = manual_data.get("reasons", []) if manual_data else []

        # Buscar warns NSFW
        nsfw_data = nsfw_warns.find_one({"guild_id": guild_id, "user_id": user.id})
        nsfw_count = nsfw_data.get("warns", 0) if nsfw_data else 0

        # Buscar imágenes violentas
        violent_data = violent_warns.find_one({"guild_id": guild_id, "user_id": user.id})
        violent_count = violent_data.get("count", 0) if violent_data else 0

        embed = discord.Embed(title=f"📋 Reporte de warns de {user}", color=discord.Color.from_rgb(0,0,0))
        embed.set_thumbnail(url=user.display_avatar.url)

        # Manual warns
        embed.add_field(name="📕 Warns manuales", value=f"{len(manual_reasons)} warn(s)", inline=False)
        if manual_reasons:
            for i, reason in enumerate(manual_reasons, 1):
                embed.add_field(name=f"#{i} - Razón", value=reason, inline=False)

        # NSFW warns
        embed.add_field(name="🔞 NSFW Warns", value=f"{nsfw_count} warn(s)", inline=False)

        # Violent content
        embed.add_field(name="🩸 Contenido violento", value=f"{violent_count} imagen(es) detectadas", inline=False)

        embed.set_footer(text=f"Solicitado por {interaction.user}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(WarnsCommand(bot))
