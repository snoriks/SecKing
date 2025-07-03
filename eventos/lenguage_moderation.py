import discord
from discord.ext import commands
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
logs_collection = db["log_channels"]
counts_collection = db["insult_counts"]

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokenizer = AutoTokenizer.from_pretrained('textdetox/xlmr-large-toxicity-classifier-v2')
        self.model = AutoModelForSequenceClassification.from_pretrained('textdetox/xlmr-large-toxicity-classifier-v2')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        try:
            inputs = self.tokenizer.encode(message.content, return_tensors="pt")
            with torch.no_grad():
                output = self.model(inputs)

            probs = torch.softmax(output.logits, dim=1)
            toxic_score = probs[0][1].item()

            if toxic_score > 0.7:
                await message.delete()

                user_id = message.author.id
                guild_id = message.guild.id

                # Incrementar insultos y warns
                user_data = counts_collection.find_one_and_update(
                    {"guild_id": guild_id, "user_id": user_id},
                    {
                        "$inc": {"count": 1, "warns": 1},
                        "$push": {"insults": message.content}
                    },
                    upsert=True,
                    return_document=True
                )

                insultos = user_data["count"] if user_data and "count" in user_data else 1
                warns = user_data["warns"] if user_data and "warns" in user_data else 1

                # Canal de logs
                log_config = logs_collection.find_one({"guild_id": guild_id})
                if log_config:
                    channel_id = log_config.get("channel_id")
                    canal = message.guild.get_channel(channel_id) if channel_id else None
                    if canal:
                        embed = discord.Embed(
                            title="🛡️ Mensaje ofensivo eliminado",
                            description=f"Mensaje eliminado por lenguaje ofensivo.",
                            color=discord.Color.red()
                        )
                        embed.add_field(name="👤 Usuario", value=f"{message.author} (`{message.author.id}`)", inline=False)
                        embed.add_field(name="💬 Contenido", value=message.content[:1024], inline=False)
                        embed.add_field(name="🚫 Total de insultos", value=str(insultos), inline=True)
                        embed.add_field(name="⚠️ Advertencias", value=str(warns), inline=True)
                        embed.add_field(name="⚙️ Score de toxicidad", value=f"{toxic_score:.2f}", inline=True)
                        embed.set_footer(text=f"Servidor: {message.guild.name}", icon_url=message.guild.icon.url if message.guild.icon else None)
                        embed.timestamp = message.created_at

                        await canal.send(embed=embed)

                        if warns >= 3:
                            await canal.send(
                                f"⚠️ {message.author.mention} ha recibido 3+ advertencias por lenguaje ofensivo. Considera tomar medidas."
                            )

                # Notificar al usuario en el canal
                embed1 = discord.Embed(
                    title="SECKING 👑",
                    description=f"{message.author.mention} tu mensaje fue eliminado por contenido ofensivo.\n"
                                f"Advertencias acumuladas: **{warns}/3**.",
                    color=discord.Color.from_rgb(0, 0, 0)
                )
                await message.channel.send(embed=embed1)

                print(f"[MODERACIÓN] ({toxic_score:.2f}): {message.content}")

        except Exception as e:
            print(f"[ERROR Moderación]: {e}")

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))
