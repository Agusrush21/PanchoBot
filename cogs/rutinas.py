import discord as ds
from discord.ext import commands, tasks
import json, os, random

nombre_actual = os.path.basename(__file__)[:-3]

class Rutinas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = os.path.abspath(os.path.join(".","cogs","configs", "rutinas_config.json"))
        self.canal_id = self.cargar_config()
        self.aviso_automatico.start()
        self.ids_canciones = []

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Módulo de {nombre_actual} cargado.")

    def cargar_config(self):
        """Lee el archivo JSON y recupera el ID guardado."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("canal_id")
        return None

    def guardar_config(self, id_canal):
        """Guarda el ID nuevo en el archivo JSON."""
        with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        data["canal_id"] = id_canal
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=4)
        self.canal_id = id_canal

    def cargar_cancion(self) -> dict:
        with open(self.config_file, "r") as f:
            data = json.load(f)
        canciones = data["biblioteca_musical"]
        
        while True:
            cancion = random.choice(canciones)
            if cancion["id"] in self.ids_canciones:
                continue

            if len(self.ids_canciones) >= len(canciones)//2:
                self.ids_canciones.pop(0), self.ids_canciones.append(cancion["id"])
            return cancion
        

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setcanal(self, ctx, canal: ds.TextChannel):
        """
        Configura el canal para los anuncios.
        """
        self.guardar_config(canal.id)
        await ctx.send(f"✅ ¡Configuración guardada! Los anuncios automáticos se enviarán a {canal.mention}.")


    @tasks.loop(minutes=30)
    async def aviso_automatico(self):
        if self.canal_id is None:
            return

        channel = self.bot.get_channel(self.canal_id)

        if channel:
            cancion = self.cargar_cancion()
            embed = ds.Embed(title=f"=== {cancion["titulo"]} ===", description=cancion["letra"], color=ds.Color.blue())
            embed.set_footer(text=f"Artista: {cancion["artista"]}")
            await channel.send(embed=embed)
        else:
            print(f"⚠ El canal con ID {self.canal_id} no fue encontrado (quizás fue borrado).")

    @aviso_automatico.before_loop
    async def antes_del_aviso(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Rutinas(bot))


if __name__ == "__main__":
    directorio = os.path.abspath("./cogs/configs")
    for a in os.listdir(directorio):
        print(a)