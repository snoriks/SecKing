import discord
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
admin_roles = db["admin_roles"]

class SetRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setrole", description="Establece el rol administrativo del bot")
    @app_commands.describe(role="Rol que tendrá acceso a comandos administrativos")
    @app_commands.checks.has_permissions(administrator=True)  
    async def setrole(self, interaction: discord.Interaction, role: discord.Role):
        # Guardar en MongoDB
        admin_roles.update_one(
            {"guild_id": interaction.guild.id},
            {"$set": {"role_id": role.id}},
            upsert=True
        )

        await interaction.response.send_message(
            f"✅ El rol {role.mention} ha sido establecido como rol administrativo del bot.",
            ephemeral=True
        )

    @setrole.error
    async def setrole_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed = discord.Embed(
                title="SECKING 👑", 
                description="❌ Solo los administradores pueden usar este comando.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="SECKING 👑",
                description="⚠️ Ocurrió un error inesperado. Si esto persiste, contacta al soporte.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            raise error

async def setup(bot: commands.Bot):
    await bot.add_cog(SetRole(bot))
