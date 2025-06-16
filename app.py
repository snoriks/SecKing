import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('token')

# Configurar intents completos
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='ks!', intents=intents)

@bot.event
async def setup_hook():
    
    for carpeta in ['eventos', 'comandos']:
        for filename in os.listdir(f'./{carpeta}'):
            if filename.endswith('.py') and not filename.startswith('__'):
                await bot.load_extension(f'{carpeta}.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f'{bot.user} ha sido encendido correctamente.')
    try:
        # Sincroniza slash commands globalmente
        synced = await bot.tree.sync()
        print(f'✅ Comandos slash sincronizados: {len(synced)}')
    except Exception as e:
        print(f'❌ Error al sincronizar comandos slash: {e}')

bot.run(token)
