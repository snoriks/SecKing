import discord
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
counts_collection = db["insult_counts"]
admin_roles = db["admin_roles"] 

class ResetInsults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="resetinsults", description="Reiniciar el contador de insultos de un usuario.")
    async def resetinsults(self, interaction: discord.Interaction, usuario: discord.Member):
        admin_config = admin_roles.find_one({"guild_id": interaction.guild.id})
        if not admin_config:
            return await interaction.response.send_message(
                "⚠️ No se ha configurado un rol administrativo con `/setrole`.",
                ephemeral=True
            )

        admin_role_id = admin_config.get("role_id")
        if not any(role.id == admin_role_id for role in interaction.user.roles):
            return await interaction.response.send_message(
                "❌ No tienes permiso para usar este comando. Se requiere el rol administrativo configurado.",
                ephemeral=True
            )

        result = counts_collection.delete_one({
            "guild_id": interaction.guild.id,
            "user_id": usuario.id
        })

        if result.deleted_count > 0:
            await interaction.response.send_message(
                f"🔄 El contador de insultos de {usuario.mention} ha sido reiniciado.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"ℹ️ {usuario.mention} no tiene registros de insultos.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ResetInsults(bot))
