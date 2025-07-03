import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import traceback
from transformers.utils import logging as hf_logging

# Silenciar logs excesivos de Hugging Face
hf_logging.set_verbosity_error()

load_dotenv()
token = os.getenv('token')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='ks!', intents=intents)

async def cargar_extensiones_recursivamente(carpeta_base):
    for root, dirs, files in os.walk(carpeta_base):
        # Ignorar carpetas __pycache__ u otras no deseadas
        dirs[:] = [d for d in dirs if d != '__pycache__']

        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                ruta_relativa = os.path.join(root, file).replace('\\', '/')
                modulo = ruta_relativa.removesuffix('.py').replace('/', '.')
                try:
                    await bot.load_extension(modulo)
                    print(f"✅ Cargado: {modulo}")
                except Exception as e:
                    print(f"❌ Error al cargar {modulo}:\n{traceback.format_exc()}")

@bot.event
async def setup_hook():
    for carpeta in ['eventos', 'comandos']:
        await cargar_extensiones_recursivamente(carpeta)

@bot.event
async def on_ready():
    print(f'{bot.user} ha sido encendido correctamente.')
    try:
        synced = await bot.tree.sync()
        print(f'✅ Comandos slash sincronizados: {len(synced)}')
    except Exception as e:
        print(f'❌ Error al sincronizar comandos slash: {e}')

bot.run(token)
