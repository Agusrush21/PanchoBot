import discord as ds
from discord.ext import commands

from parametros import COMMAND

import os
nombre_actual = os.path.basename(__file__)[:-3]


class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Módulo de {nombre_actual} cargado.")

    @commands.command(name="help", aliases=["ayuda", "comandos", "h"])
    async def ayuda(self, ctx):
        """Muestra esta lista de comandos."""
        
        # Creamos el Embed base
        embed = ds.Embed(
            title="🤖 Lista de Comandos",
            description=f"Usa `{COMMAND}comando` para ejecutar una acción.",
            color=ds.Color.gold()
        )
        
        for nombre_cog, cog in self.bot.cogs.items():
            lista_comandos_texto = ""
            
            for comando in cog.get_commands():
                if comando.hidden:
                    continue
                
                descripcion = comando.help if comando.help else "Sin descripción disponible."
                
                lista_comandos_texto += f"**{COMMAND}{comando.name}** - {descripcion}\n"
            
            if lista_comandos_texto:
                embed.add_field(name=f"📂 {nombre_cog}", value=lista_comandos_texto, inline=False)
        
        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ayuda(bot))