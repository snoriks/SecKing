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
counts_collection = db["insult_counts"]
admin_roles = db["admin_roles"]  

class WarnsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="warns", description="Ver los warns acumulados de un usuario")
    @app_commands.describe(user="El usuario al que quieres consultar los warns")
    async def warns(self, interaction: discord.Interaction, user: discord.Member):
        guild_id = interaction.guild.id

        admin_config = admin_roles.find_one({"guild_id": guild_id})
        if not admin_config:
            return await interaction.response.send_message(
                "⚠️ No se ha establecido un rol administrativo con `/setrole`.",
                ephemeral=True
            )

        admin_role_id = admin_config.get("role_id")
        has_permission = any(role.id == admin_role_id for role in interaction.user.roles)
        if not has_permission:
            return await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando. Se requiere el rol administrativo configurado.",
                ephemeral=True
            )

        # Warns manuales
        manual_data = manual_warns.find_one({"guild_id": guild_id, "user_id": user.id})
        manual_reasons = manual_data.get("reasons", []) if manual_data else []

        # NSFW
        nsfw_data = nsfw_warns.find_one({"guild_id": guild_id, "user_id": user.id})
        nsfw_count = nsfw_data.get("warns", 0) if nsfw_data else 0

        # Violencia
        violent_data = violent_warns.find_one({"guild_id": guild_id, "user_id": user.id})
        violent_count = violent_data.get("count", 0) if violent_data else 0

        # Lenguaje ofensivo
        toxic_data = counts_collection.find_one({"guild_id": guild_id, "user_id": user.id})
        toxic_warns = toxic_data.get("warns", 0) if toxic_data else 0

        # Embed de resumen
        embed = discord.Embed(title=f"📋 Reporte de warns de {user}", color=discord.Color.from_rgb(0, 0, 0))
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="📕 Warns manuales", value=f"{len(manual_reasons)} warn(s)", inline=False)
        if manual_reasons:
            for i, reason in enumerate(manual_reasons, 1):
                embed.add_field(name=f"#{i} - Razón", value=reason, inline=False)

        embed.add_field(name="🔞 NSFW Warns", value=f"{nsfw_count} warn(s)", inline=False)
        embed.add_field(name="🩸 Contenido violento", value=f"{violent_count} imagen(es) detectadas", inline=False)
        embed.add_field(name="💬 Lenguaje ofensivo", value=f"{toxic_warns} advertencia(s)", inline=False)

        embed.set_footer(text=f"Solicitado por {interaction.user}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(WarnsCommand(bot))
