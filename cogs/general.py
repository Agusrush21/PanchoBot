import discord as ds
from discord.ext import commands

import os, time
from random import choice

nombre_actual = os.path.basename(__file__)[:-3]


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mensajes = ["QUE PASA CAUSA ¡¡¡GAAAAAAAAAAAAAAAAA!!!", "Que hablai bonito ''"]

    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Módulo de {nombre_actual} cargado.")

    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions:
            mensaje = choice(self.mensajes)
            mensaje = mensaje.replace("''", message.author.mention)
            await message.channel.send(mensaje)


    @commands.command()
    async def ping(self, ctx):
        """Muestra la latencia del bot y de la API."""
        
        # 1. Obtenemos la latencia del WebSocket (en ms)
        latencia_ws = round(self.bot.latency * 1000)
        
        # 2. Medimos cuánto tarda en enviar un mensaje (Latencia de API)
        inicio = time.perf_counter()
        mensaje = await ctx.send(f"🏓 Pong! Calculando...")
        fin = time.perf_counter()
        
        latencia_api = round((fin - inicio) * 1000)
        
        # 3. Editamos el mensaje con los resultados finales
        embed = ds.Embed(title="🏓 Pong!", color=ds.Color.green())
        embed.add_field(name="📡 Latencia WebSocket", value=f"`{latencia_ws}ms`", inline=True)
        embed.add_field(name="⚡ Latencia API", value=f"`{latencia_api}ms`", inline=True)
        
        await mensaje.edit(content=None, embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))