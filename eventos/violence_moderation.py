import discord
from discord.ext import commands
from PIL import Image
from io import BytesIO
import torch
from transformers import ViTFeatureExtractor, ViTForImageClassification
from pymongo import MongoClient
import os
import requests
from dotenv import load_dotenv

load_dotenv()
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["secking"]
logs_collection = db["log_channels"]
violence_collection = db["violent_images"]

class ModeracionViolencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fe = ViTFeatureExtractor.from_pretrained("jaranohaal/vit-base-violence-detection")
        self.model = ViTForImageClassification.from_pretrained("jaranohaal/vit-base-violence-detection")
        
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.attachments:
            return
        
        for att in message.attachments:
            if att.filename.lower().endswith(('.png','.jpg','.jpeg','.webp')):
                try:
                    img = Image.open(BytesIO(requests.get(att.url).content)).convert("RGB")
                    inputs = self.fe(images=img, return_tensors="pt")
                    with torch.no_grad():
                        logits = self.model(**inputs).logits
                        probs = torch.softmax(logits, dim=1)[0]
                        idx = probs.argmax().item()
                        label = self.model.config.id2label[idx].lower()
                        conf = probs[idx].item()

                    print(f"[VIOLENCIA] {label} ({conf:.2f}) por {message.author}")

                    if label == "violent" and conf > 0.85:
                        await message.delete()
                        vio = violence_collection.find_one_and_update(
                            {"guild_id": message.guild.id, "user_id": message.author.id},
                            {"$inc": {"count": 1}},
                            upsert=True,
                            return_document=True
                        )
                        total = vio.get("count", 1)

                        lc = logs_collection.find_one({"guild_id": message.guild.id})
                        ch = message.guild.get_channel(lc["channel_id"]) if lc else None
                        if ch:
                            e = discord.Embed(
                                title="🚨 Imagen violenta eliminada",
                                description=f"{message.author.mention} envió contenido violento.",
                                color=discord.Color.from_rgb(0,0,0)
                            )
                            e.add_field(name="📈 Confianza", value=f"{conf:.2f}", inline=True)
                            e.add_field(name="🔢 Conteo", value=str(total), inline=True)
                            e.set_image(url=att.url)
                            e.timestamp = message.created_at
                            await ch.send(embed=e)

                            if total >= 3:
                                await ch.send(
                                    f"⚠️ {message.author.mention} alcanzó 3+ contenidos violentos. ⚠️"
                                )

                        try:
                            await message.author.send(
                                f"Tu imagen fue eliminada en **{message.guild.name}** por violencia. "
                                "Continúa en contacto con un administrador si persistente."
                            )
                        except discord.Forbidden:
                            pass

                except Exception as err:
                    print(f"[ERROR Violencia]: {err}")

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(ModeracionViolencia(bot))
