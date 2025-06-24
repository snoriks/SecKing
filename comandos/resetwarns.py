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

class ResetWarns(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="resetwarns", description="Reiniciar warns de un usuario")
    @app_commands.describe(
        user="Usuario al que deseas modificar los warns",
        category="Tipo de warns a reiniciar",
        amount="Cantidad de warns a eliminar (0 para reiniciar todo)"
    )
    @app_commands.choices(category=[
        app_commands.Choice(name="Manual (comando /warn)", value="manual"),
        app_commands.Choice(name="NSFW (contenido sexual)", value="nsfw"),
        app_commands.Choice(name="Violencia (sangre, armas, etc.)", value="violence")
    ])
    async def resetwarns(self, interaction: discord.Interaction, user: discord.Member, category: app_commands.Choice[str], amount: int):
        guild_id = interaction.guild.id
        tipo = category.value

        if amount < 0:
            return await interaction.response.send_message("La cantidad no puede ser negativa.", ephemeral=True)

        if tipo == "manual":
            data = manual_warns.find_one({"guild_id": guild_id, "user_id": user.id})
            reasons = data.get("reasons", []) if data else []
            if amount == 0 or amount >= len(reasons):
                manual_warns.delete_one({"guild_id": guild_id, "user_id": user.id})
                msg = "todos los warns manuales"
            else:
                updated = reasons[:-amount]
                manual_warns.update_one(
                    {"guild_id": guild_id, "user_id": user.id},
                    {"$set": {"reasons": updated}}
                )
                msg = f"los últimos {amount} warns manuales"

        elif tipo == "nsfw":
            data = nsfw_warns.find_one({"guild_id": guild_id, "user_id": user.id})
            count = data.get("warns", 0) if data else 0
            if amount == 0 or amount >= count:
                nsfw_warns.update_one(
                    {"guild_id": guild_id, "user_id": user.id},
                    {"$set": {"warns": 0}}, upsert=True
                )
                msg = "todos los warns NSFW"
            else:
                nsfw_warns.update_one(
                    {"guild_id": guild_id, "user_id": user.id},
                    {"$inc": {"warns": -amount}}
                )
                msg = f"{amount} warns NSFW"

        elif tipo == "violence":
            data = violent_warns.find_one({"guild_id": guild_id, "user_id": user.id})
            count = data.get("count", 0) if data else 0
            if amount == 0 or amount >= count:
                violent_warns.update_one(
                    {"guild_id": guild_id, "user_id": user.id},
                    {"$set": {"count": 0}}, upsert=True
                )
                msg = "todos los registros de violencia"
            else:
                violent_warns.update_one(
                    {"guild_id": guild_id, "user_id": user.id},
                    {"$inc": {"count": -amount}}
                )
                msg = f"{amount} registros de violencia"

        await interaction.response.send_message(
            f"✅ Se han eliminado {msg} de {user.mention}.", ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ResetWarns(bot))
