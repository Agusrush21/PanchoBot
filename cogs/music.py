import discord as ds
from discord.ext import commands
import yt_dlp, math, asyncio

from parametros import COMMAND, TIMEOUT, TIMEOUT_NO_MUSIC

import os
nombre_actual = os.path.basename(__file__)[:-3]


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.colas = {} # Format -> {id_server: [{url, title}, {url, title}, ...], ...}
        self.contador = 0

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Módulo de {nombre_actual} cargado.")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.guild.voice_client:
            return
        
        voice_client = member.guild.voice_client

        if voice_client.channel and len(voice_client.channel.members) == 1:
            print(f"Me he quedado solo. Me desconectaré en {TIMEOUT}s si nadie vuelve.")
            
            await asyncio.sleep(TIMEOUT)

            if voice_client.is_connected() and len(voice_client.channel.members) == 1:
                await voice_client.disconnect()
                
                id_servidor = member.guild.id
                if id_servidor in self.colas:
                    self.colas[id_servidor] = []
                    
                print("Me desconecté por inactividad.")


    def revisar_cola(self, ctx, error=None):
        if error:
            print(f"Error al reproducir: {error}")

        self.bot.loop.create_task(self.tocar_siguiente(ctx))

    async def tocar_siguiente(self, ctx):
        id_servidor = ctx.guild.id
        voice_client = ctx.guild.voice_client

        if id_servidor in self.colas and len(self.colas[id_servidor]) > 0:

            cancion = self.colas[id_servidor].pop(0)
            
            ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            source = ds.FFmpegPCMAudio(cancion['url'], **ffmpeg_options)
            
            voice_client.play(source, after=lambda e: self.revisar_cola(ctx, error=e))

        else:
            
            if voice_client and voice_client.is_connected():
                await asyncio.sleep(TIMEOUT_NO_MUSIC)

                if voice_client.is_connected() and not voice_client.is_playing():
                    
                    if id_servidor in self.colas:
                        del self.colas[id_servidor]
                    
                    await voice_client.disconnect()

                    embed = ds.Embed(
                        description=f"💤 Me he desconectado por inactividad. ¡Usa `{COMMAND}play` para llamarme de nuevo!",
                        color=ds.Color.red()
                    )
                    await ctx.send(embed=embed)

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, search):
        """Busca y agrega una canción para reproducir"""
        if not ctx.author.voice:
            return await ctx.send("❌ ¡Entra a un canal de voz primero!")
        
        if not ctx.guild.voice_client:
            await ctx.author.voice.channel.connect()

        voice_client = ctx.guild.voice_client

        ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True}
        
        msg = await ctx.send(f"🔎 Buscando: `{search}`...")

        try:
            if "https://" in search or "http://" in search or "www." in search:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(search, download=False)
                    
                    if 'entries' in info:
                        info = info['entries'][0]
                        
            else:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]

            url_audio = info['url']
            title = info['title']
            
            datos_cancion = {'url': url_audio, 'title': title}

            if voice_client.is_playing():
                id_servidor = ctx.guild.id
                
                if id_servidor not in self.colas:
                    self.colas[id_servidor] = []
                
                self.colas[id_servidor].append(datos_cancion)
                await msg.edit(content=f"📝 **Añadido a la cola:** {title}")
                
            else:
                ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
                source = ds.FFmpegPCMAudio(url_audio, **ffmpeg_options)
                
                # Iniciamos el ciclo
                voice_client.play(source, after=lambda e: self.revisar_cola(ctx, error=e))
                await msg.edit(content=f"▶️ **Reproduciendo:** {title}")

        except Exception as e:
            await ctx.send(f"Ocurrió un error: {e}")

    
    @commands.command(aliases=["saltar", "next", "siguiente", "s"])
    async def skip(self, ctx):
        """Salta a la siguiente canción"""
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop() 
            await ctx.send("⏭️ Canción saltada.")
        else:
            await ctx.send("No hay nada sonando.")


    @commands.command(aliases=["pausa"])
    async def pause(self, ctx):
        """Pausa la canción actual"""
        voice_client = ctx.guild.voice_client
        
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("⏸️ Música pausada.")
        elif voice_client and voice_client.is_paused():
            await ctx.send(f"¡La música ya está pausada! Usa `{COMMAND}resume` para continuar.")
        else:
            await ctx.send("No estoy tocando nada en este momento.")

    
    @commands.command(aliases=["r"])
    async def resume(self, ctx):
        """Reanuda la canción actual"""
        voice_client = ctx.guild.voice_client
        
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("▶️ Reanudando la música.")
        elif voice_client and voice_client.is_playing():
            await ctx.send("¡La música ya está sonando!")
        else:
            await ctx.send("No hay nada que reanudar.")

    
    @commands.command(aliases=["l"])
    async def leave(self, ctx):
        """Sacas al bot del canal de voz"""
        voice_client = ctx.guild.voice_client
        
        if voice_client:
            id_servidor = ctx.guild.id
            if id_servidor in self.colas:
                self.colas[id_servidor] = []
            
            await voice_client.disconnect()
            await ctx.send("👋 ¡Nos vemos! Me he desconectado.")
        else:
            await ctx.send("No estoy conectado a ningún canal de voz.")


    @commands.command(aliases=["para", "parar"])
    async def stop(self, ctx):
        """Para todas las canciones activas"""
        voice_client = ctx.guild.voice_client
        
        if voice_client:
            id_servidor = ctx.guild.id
            self.colas[id_servidor] = []
            
            voice_client.stop()
            await ctx.send("🛑 Reproducción detenida y cola vaciada.")

    
    @commands.command(aliases=["q", "lista", "tail", "cola"])
    async def queue(self, ctx, page: int = 1):
        """Revisa la lista de canciones"""
        id_servidor = ctx.guild.id
        
        if id_servidor not in self.colas or len(self.colas[id_servidor]) == 0:
            return await ctx.send("La cola está vacía.")

        lista_canciones = self.colas[id_servidor]
        canciones_por_pagina = 10
        
        total_paginas = math.ceil(len(lista_canciones) / canciones_por_pagina)

        if page < 1 or page > total_paginas:
            return await ctx.send(f"Esa página no existe. Solo hay {total_paginas} páginas.")

        inicio = (page - 1) * canciones_por_pagina
        fin = inicio + canciones_por_pagina
        canciones_pagina = lista_canciones[inicio:fin]

        descripcion = ""
        for i, cancion in enumerate(canciones_pagina, inicio + 1):
            descripcion += f"`{i}.` {cancion['title']}\n"

        embed = ds.Embed(
            title=f"🎵 Cola de Reproducción - {len(lista_canciones)} canciones",
            description=descripcion,
            color=ds.Color.blue()
        )
        

        embed.set_footer(text=f"Página {page}/{total_paginas} | Usa !queue [numero] para ver más")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Music(bot))
        