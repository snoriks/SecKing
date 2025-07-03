import discord
from discord import app_commands
from discord.ext import commands
from dpy_paginator import paginate
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
counts_collection = db["insult_counts"]
admin_roles = db["admin_roles"] 

class InfoInsults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="infoinsults", description="Muestra el historial de insultos de un usuario en este servidor.")
    async def infoinsults(self, interaction: discord.Interaction, usuario: discord.Member):
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

        # Obtener historial de insultos
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

        # Paginar insultos
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

        paginator = paginate(embeds=embeds)
        await interaction.response.send_message(embed=paginator.embed, view=paginator.view, ephemeral=True)

    @infoinsults.error
    async def infoinsults_error(self, interaction: discord.Interaction, error):
        embed = discord.Embed(
            title="SECKING 👑",
            color=discord.Color.from_rgb(0, 0, 0)
        )

        if isinstance(error, app_commands.errors.MissingPermissions):
            embed.description = "¿Qué intentas hacer?\nSolo personal autorizado puede usar este comando."
        else:
            embed.description = (
                "Ocurrió un error al generar el historial.\n"
                "Si esto continúa, contacta al soporte del Discord oficial de **SecKing**."
            )
            raise error

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(InfoInsults(bot))
