import discord
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
logs_collection = db["log_channels"]

class SetLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setlog", description="Configura el canal donde se enviarán los logs de moderación.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlog(self, interaction: discord.Interaction, canal: discord.TextChannel):
        logs_collection.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {"channel_id": canal.id}},
            upsert=True
        )

        await interaction.response.send_message(
            f"✅ Canal de logs configurado correctamente: {canal.mention}",
            ephemeral=True
        )

    @setlog.error
    async def setlog_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("🚫 Solo administradores pueden usar este comando.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Ocurrió un error inesperado.", ephemeral=True)
            raise error

async def setup(bot):
    await bot.add_cog(SetLog(bot))
