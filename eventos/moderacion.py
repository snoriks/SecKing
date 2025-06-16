from discord.ext import commands
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Cargar el modelo y el tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained('textdetox/xlmr-large-toxicity-classifier-v2')
        self.model = AutoModelForSequenceClassification.from_pretrained('textdetox/xlmr-large-toxicity-classifier-v2')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        try:
            # Tokenizar el mensaje
            inputs = self.tokenizer.encode(message.content, return_tensors="pt")
            with torch.no_grad():
                output = self.model(inputs)

            # Obtener probabilidades con softmax
            probs = torch.softmax(output.logits, dim=1)
            toxic_score = probs[0][1].item()  # Índice 1 es "toxic"

            if toxic_score > 0.7:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, tu mensaje fue eliminado por contenido ofensivo."
                )
                print(f"[MODERACIÓN] TOXICIDAD ({toxic_score:.2f}): {message.content}")

        except Exception as e:
            print(f"[ERROR Moderación]: {e}")

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))
