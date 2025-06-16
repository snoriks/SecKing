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
                
                # Incremento del conteo
                user_id = message.author.id
                guild_id = message.guild.id
                user_data = counts_collection.find_one_and_update(
                    {"guild_id": guild_id, "user_id": user_id},
                    {"$inc": {"count": 1}},
                    upsert=True,
                    return_document=True
                )
                insultos = user_data["count"] if user_data and "count" in user_data else 1

                # Obtener canal de logs
                log_config = logs_collection.find_one({"guild_id": guild_id})
                if log_config:
                    channel_id = log_config.get("channel_id")
                    if channel_id:
                        canal = message.guild.get_channel(channel_id)
                        if canal:
                            await canal.send(
                                f"**Log - Language Moderation**\n"
                                f"👤 Usuario: `{message.author} ({message.author.id})`\n"
                                f"💬 Mensaje: `{message.content}`\n"
                                f"🚫 Cuántas veces ha insultado: **{insultos}**"
                            )

                # Aviso al canal de origen
                await message.channel.send(
                    f"⚠️ {message.author.mention}, tu mensaje fue eliminado por contenido ofensivo."
                )
                print(f"[MODERACIÓN] TOXICIDAD ({toxic_score:.2f}): {message.content}")

        except Exception as e:
            print(f"[ERROR Moderación]: {e}")

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))
