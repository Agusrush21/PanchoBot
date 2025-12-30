import os, asyncio
from dotenv import load_dotenv

import discord as ds
from discord.ext import commands

from parametros import COMMAND
import webserver

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = ds.Intents.default()
intents.message_content = True # Para leer comandos

bot = commands.Bot(command_prefix=COMMAND, intents=intents, help_command=None)

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    # bot.user.name = "PicoQuienLoLea"
    mensaje = f"✅ Logueado como {bot.user} (ID: {bot.user.id})"
    print(mensaje)
    print((len(mensaje)+1)*'-')

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == '__main__':
    try:

        asyncio.run(main())
    except KeyboardInterrupt:
        # Permite cerrar el bot con Ctrl+C sin errores feos
        pass