import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()


token = os.getenv('token')


intents = discord.Intents.all()
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='ks!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} ha sido encendido correctamente.')

@bot.event
async def setup_hook():
    for filename in os.listdir('./eventos'):
        if filename.endswith('.py'):
            await bot.load_extension(f'eventos.{filename[:-3]}') #sin .py

#ejecución del bot.
bot.run(token)