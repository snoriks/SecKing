import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
user_warns = db["manual_warns"]

class WarnActionsView(View):
    def __init__(self, user: discord.Member):
        super().__init__(timeout=60)
        self.user = user

    @discord.ui.button(label="Banear", style=discord.ButtonStyle.danger)
    async def banear(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.ban_members:
            await self.user.ban(reason="Sistema de warns acumulados")
            await interaction.response.send_message(f"🔨 {self.user.mention} ha sido **baneado**.", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message("No tienes permisos para banear.", ephemeral=True)

    @discord.ui.button(label="Suspender", style=discord.ButtonStyle.secondary)
    async def suspender(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔧 Suspensión aplicada (acción personalizada).", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Expulsar", style=discord.ButtonStyle.primary)
    async def expulsar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.kick_members:
            await self.user.kick(reason="Sistema de warns acumulados")
            await interaction.response.send_message(f"🚪 {self.user.mention} ha sido **expulsado**.", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message("No tienes permisos para expulsar.", ephemeral=True)

class WarnCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Aplicar un warn a un usuario con razón obligatoria.")
    @app_commands.describe(user="Usuario a advertir", reason="Razón del warn")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not interaction.user.guild_permissions.kick_members and not interaction.user.guild_permissions.ban_members:
            return await interaction.response.send_message("🚫 No tienes permisos para usar este comando.", ephemeral=True)

        warn_data = user_warns.find_one({"guild_id": interaction.guild.id, "user_id": user.id})

        if warn_data:
            reasons = warn_data.get("reasons", [])
            reasons.append(reason)
            total_warns = len(reasons)
            user_warns.update_one(
                {"guild_id": interaction.guild.id, "user_id": user.id},
                {"$set": {"reasons": reasons}}
            )
        else:
            reasons = [reason]
            total_warns = 1
            user_warns.insert_one({
                "guild_id": interaction.guild.id,
                "user_id": user.id,
                "reasons": reasons
            })

        await interaction.response.send_message(f"⚠️ Se ha aplicado un warn a {user.mention} (Total: {total_warns}/3)", ephemeral=True)

        if total_warns >= 3:
            embed = discord.Embed(
                title=f"🚨 WARNS - {user}",
                description=f"**Warn aplicado por:** {interaction.user.mention}",
                color=discord.Color.from_rgb(0,0,0)
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Usuario ID: {user.id}")

            for i, r in enumerate(reasons, start=1):
                embed.add_field(name=f"#{i} - Razón", value=r, inline=False)

            await interaction.channel.send(embed=embed, view=WarnActionsView(user))

async def setup(bot: commands.Bot):
    await bot.add_cog(WarnCommand(bot))
