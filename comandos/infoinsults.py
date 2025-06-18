import discord
from discord import app_commands
from discord.ext import commands
from dpy_paginator import paginate
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import tempfile

load_dotenv()
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
counts_collection = db["insult_counts"]

class InfoInsults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="infoinsults", description="Muestra el historial de insultos de un usuario en este servidor.")
    @app_commands.checks.has_permissions(administrator=True)
    async def infoinsults(self, interaction: discord.Interaction, usuario: discord.Member):
        record = counts_collection.find_one({
            "guild_id": interaction.guild.id,
            "user_id": usuario.id
        })
        insults = record.get("insults", []) if record else []
        count = len(insults)

        if count == 0:
            return await interaction.response.send_message(
                f"ℹ️ {usuario.mention} no ha sido marcado como ofensivo en este servidor.",
                ephemeral=True
            )

        embeds = []
        per_page = 5
        total_pages = (count + per_page - 1) // per_page

        for page in range(total_pages):
            start = page * per_page
            slice_msgs = insults[start:start + per_page]
            description = "\n".join(f"**#{start + idx + 1}** – {msg}" for idx, msg in enumerate(slice_msgs))
            embed = discord.Embed(
                title=f"Historial de insultos de {usuario}",
                description=description,
                color=discord.Color.from_rgb(0, 0, 0)
            )
            embed.set_footer(text=f"Página {page + 1}/{total_pages}")
            embeds.append(embed)

        pm = paginate(embeds=embeds)

        await interaction.response.send_message(embed=pm.embed, view=pm.view, ephemeral=True)

    @infoinsults.error
    async def infoinsults_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed = discord.Embed(
                title="SECKING 👑",
                description="¿Qué intentas hacer?\nSolo administradores pueden usar este comando.",
                color=discord.Color.from_rgb(0, 0, 0)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="SECKING 👑",
                description="Ocurrió un error al generar el historial.\nSi esto continua escribele a soporte en el discord oficial de **SecKing**",
                color=discord.Color.from_rgb(0, 0, 0)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            raise error

async def setup(bot):
    await bot.add_cog(InfoInsults(bot))
