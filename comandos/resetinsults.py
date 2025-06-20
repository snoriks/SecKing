import discord
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo ["secking"]
counts_collection = db ["insult_counts"]


class ResetInsults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    
    @app_commands.command(name="resetinsults", description= "Reiniciar el contador de insultos de un usuario.")
    @app_commands.checks.has_permissions(administrator=True)
    async def resetinsults (self, interaction: discord.Interaction, usuario: discord.Member):
        result = counts_collection.delete_one({
            "guild_id": interaction.guild.id,
            "user_id": usuario.id
        })
        
        if result.deleted_count > 0:
            await interaction.response.send_message(f"🔄 El contador de insultos de {usuario.mention} ha sido reiniciado.", 
            ephemeral=True
        )
    
    @resetinsults.error
    async def resetinsults_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed = discord.Embed(
                title="SECKING",
                description="¿Qué intentas hacer? solo administradores pueden usar este comando",
                color=discord.Color.from_rgb(0,0,0)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed1 = discord.Embed(
                title="SECKING",
                description="Ocurrio un error inesperado, si esto continúa contacta con soporte en el discord oficial.",
                color=discord.Color.from_rgb(0,0,0)
            )
            await interaction.response.send_message(embed=embed1, ephemeral=True)
            raise error

async def setup(bot):
    await bot.add_cog(ResetInsults(bot))
