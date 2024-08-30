import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp as youtube_dl
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Configure yt-dlp for downloading and processing YouTube audio streams
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'cookiefile': 'cookies.txt'  # Add this line for authentication
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take the first item from a playlist or a list
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id='93fce145f08a4f9a82a18567d0adb10a',
            client_secret='ad88b92087744c438561f452e734d067'
        ))

    @app_commands.command(name='join', description='Join a voice channel.')
    async def join(self, interaction: discord.Interaction):
        """Joins a voice channel."""
        if interaction.user.voice is not None:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message("Joined the voice channel.")
        else:
            await interaction.response.send_message("You're not connected to a voice channel!")

    @app_commands.command(name='leave', description='Leave the voice channel.')
    async def leave(self, interaction: discord.Interaction):
        """Leaves the voice channel."""
        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Left the voice channel.")
        else:
            await interaction.response.send_message("I'm not in a voice channel!")

    async def get_spotify_url(self, url):
        track_id = url.split('/')[-1].split('?')[0]
        track = self.sp.track(track_id)
        query = f"{track['name']} - {track['artists'][0]['name']}"
        return query

    @app_commands.command(name='play', description='Play a song from a URL (YouTube, Spotify, etc.).')
    async def play(self, interaction: discord.Interaction, url: str):
        """Plays a song from a URL (YouTube, etc.)."""
        await interaction.response.defer(ephemeral=False)
        if 'spotify.com' in url:
            url = await self.get_spotify_url(url)
        
        if interaction.guild.voice_client is None:
            await interaction.user.voice.channel.connect()

        
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        self.song_queue.append(player)
            
        if not interaction.guild.voice_client.is_playing():
            await self.play_next(interaction)

    async def play_next(self, interaction: discord.Interaction):
        if self.song_queue:
            player = self.song_queue.pop(0)
            interaction.guild.voice_client.play(player, after=lambda e: self.bot.loop.create_task(self.play_next(interaction)))
            await interaction.followup.send(f'Now playing: {player.title}')
        else:
            await interaction.followup.send("Queue is empty.")

    @app_commands.command(name='pause', description='Pause the currently playing song.')
    async def pause(self, interaction: discord.Interaction):
        """Pauses the currently playing song."""
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("Music paused.")
        else:
            await interaction.response.send_message("No music is currently playing.")

    @app_commands.command(name='resume', description='Resume the currently paused song.')
    async def resume(self, interaction: discord.Interaction):
        """Resumes the currently paused song."""
        if interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("Music resumed.")
        else:
            await interaction.response.send_message("The music isn't paused.")

    @app_commands.command(name='stop', description='Stop the currently playing song.')
    async def stop(self, interaction: discord.Interaction):
        """Stops the currently playing song."""
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Music stopped.")

    @app_commands.command(name='skip', description='Skip the currently playing song.')
    async def skip(self, interaction: discord.Interaction):
        """Skips the currently playing song."""
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("Skipped the song.")
        else:
            await interaction.response.send_message("No music is currently playing.")

   # @play.before_invoke
 #   async def ensure_voice(self, interaction: discord.Interaction):
  #      if interaction.guild.voice_client is None:
    #        if interaction.user.voice:
   ##             await interaction.user.voice.channel.connect()
   #         else:
  # #             await interaction.response.send_message("You are not connected to a voice channel.")
    #            raise commands.CommandError("Author not connected to a voice channel.")
    #    elif interaction.guild.voice_client.is_playing():
     #       interaction.guild.voice_client.stop()


# Add the Cog to the bot
async def setup(bot):
    await bot.add_cog(Music(bot) ,guilds=[discord.Object(id='1246531747106132060') , discord.Object(id='820326376673771540')])
