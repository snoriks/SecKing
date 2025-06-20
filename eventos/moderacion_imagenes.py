import discord
from discord.ext import commands
from PIL import Image
from io import BytesIO
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from pymongo import MongoClient
import os
import requests
from dotenv import load_dotenv

load_dotenv()
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
logs_collection = db["log_channels"]
warns_collection = db["image_warns"]
violence_collection = db["violent_images"]

class ModeracionImagenes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.processor = AutoImageProcessor.from_pretrained("Falconsai/nsfw_image_detection")
        self.model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.attachments:
            return

        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                try:
                    response = requests.get(attachment.url)
                    image = Image.open(BytesIO(response.content)).convert("RGB")

                    inputs = self.processor(images=image, return_tensors="pt")
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        probs = torch.softmax(outputs.logits, dim=1)[0]
                        predicted_class = probs.argmax().item()
                        labels = self.model.config.id2label
                        label = labels[predicted_class].lower()
                        confidence = probs[predicted_class].item()

                    print(f"[IMAGEN DETECTADA] {label} ({confidence:.2f}) por {message.author}")

                    is_nsfw = label in ["porn", "hentai", "sexy", "nsfw", "drawing"]
                    is_violenta = label in ["weapon", "gore", "bloody", "violence"]

                    log_config = logs_collection.find_one({"guild_id": message.guild.id})
                    canal_logs = message.guild.get_channel(log_config["channel_id"]) if log_config else None

                    # NSFW
                    if is_nsfw and confidence > 0.85:
                        await message.delete()

                        warn_data = warns_collection.find_one_and_update(
                            {"guild_id": message.guild.id, "user_id": message.author.id},
                            {"$inc": {"warns": 1}},
                            upsert=True,
                            return_document=True
                        )
                        total_warns = warn_data["warns"] if warn_data and "warns" in warn_data else 1

                        if canal_logs:
                            embed = discord.Embed(
                                title="Image Moderation Logs - NSFW 📜",
                                description=f"{message.author.mention} envió contenido NSFW.",
                                color=discord.Color.red()
                            )
                            embed.add_field(name="🧪 Categoría", value=label, inline=True)
                            embed.add_field(name="📈 Confianza", value=f"{confidence:.2f}", inline=True)
                            embed.add_field(name="🔢 Warns acumulados", value=str(total_warns), inline=True)
                            embed.set_image(url=attachment.url)
                            embed.timestamp = message.created_at
                            await canal_logs.send(embed=embed)

                            if total_warns >= 3:
                                await canal_logs.send(
                                    f"🚨 {message.author.mention} ha superado los 3 warns por imágenes NSFW. "
                                    f"Se recomienda que un administrador revise al usuario."
                                )

                        try:
                            await message.author.send(
                                f"Tu imagen fue eliminada de **{message.guild.name}** por contenido NSFW.\n"
                                f"Advertencias acumuladas: **{total_warns}/3**."
                            )
                        except discord.Forbidden:
                            pass

                    elif is_violenta and confidence > 0.85:
                        await message.delete()

                        # Registrar en base de datos cuántas veces ha enviado contenido violento
                        violent_data = violence_collection.find_one_and_update(
                            {"guild_id": message.guild.id, "user_id": message.author.id},
                            {"$inc": {"count": 1}},
                            upsert=True,
                            return_document=True
                        )
                        total_violentas = violent_data["count"] if violent_data and "count" in violent_data else 1

                        if canal_logs:
                            embed = discord.Embed(
                                title="Logs Image Moderation - Violent 📜",
                                description=f"{message.author.mention} envió contenido violento.",
                                color=discord.Color.orange()
                            )
                            embed.add_field(name="🧪 Categoría", value=label, inline=True)
                            embed.add_field(name="📈 Confianza", value=f"{confidence:.2f}", inline=True)
                            embed.add_field(name="🔢 Reportes de violencia", value=str(total_violentas), inline=True)
                            embed.set_image(url=attachment.url)
                            embed.timestamp = message.created_at
                            await canal_logs.send(embed=embed)

                            if total_violentas >= 3:
                                await canal_logs.send(
                                    f"⚠️ {message.author.mention} ha enviado 3+ imágenes violentas. "
                                    f"Recomendamos que un administrador revise su actividad."
                                )

                        try:
                            await message.author.send(
                                f"Tu imagen fue eliminada de **{message.guild.name}** por contener contenido violento (`{label}`).\n"
                                f"No se te aplicó advertencia oficial, pero fue registrado.\n"
                                f"⚠️ Si continúas compartiendo este tipo de contenido, un administrador podría sancionarte o banearte."
                            )
                        except discord.Forbidden:
                            pass

                except Exception as e:
                    print(f"[ERROR Moderación Imágenes]: {e}")

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(ModeracionImagenes(bot))
