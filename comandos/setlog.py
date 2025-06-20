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
        embed = discord.Embed(
            title="SECKING 👑",
            description=f"El canal de logs fue configurado correctamente: {canal.mention}",
            color=discord.Color.from_rgb(0,0,0)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @setlog.error
    async def setlog_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed = discord.Embed(
                title="SECKING 👑", 
                description="¿Qué intentas hacer? solo administradores pueden usar este comando...",
                color=discord.Color.from_rgb(0,0,0)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed1 = discord.Embed(
                title="SECKING 👑",
                description="Ocurrio un error inesperado, si esto continúa contacta con soporte en el discord oficial.",
                color=discord.Color.from_rgb(0,0,0)
            )
            await interaction.response.send_message(embed=embed1, ephemeral=True)
            raise error

async def setup(bot):
    await bot.add_cog(SetLog(bot))
