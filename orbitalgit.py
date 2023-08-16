import discord
from discord.ext import commands, tasks
import random
from youtubesearchpython import VideosSearch
from pytube import YouTube
import asyncio
import os

# Define the intents your bot will use
intents = discord.Intents.default()
intents.voice_states = True
intents.messages = True  # Add this line to enable message content intent
intents.message_content = True

bot = commands.Bot(command_prefix=';', intents=intents)

# Define radio sources
radio_sources = {
    'orbital': 'https://ec2.yesstreaming.net:3025/stream',
    'comercial': 'https://stream-icy.bauermedia.pt/comercial.mp3?listening-from-radio-garden=1692094786',
    'antena1': 'https://radiocast.rtp.pt/antena180a.mp3?listening-from-radio-garden=1692095173',
    'm80': 'https://stream-icy.bauermedia.pt/m80.mp3?listening-from-radio-garden=1692095652',
    'rfm': 'https://radio.garden/api/ara/content/listen/Ejy5Gaa6/channel.mp3?r=1&1692118912063',
    'renascença': 'https://radio.garden/api/ara/content/listen/mYZdSKn8/channel.mp3?r=1&1692119223824'
}

current_radio = None  # Stores the currently playing radio source
song_queue = []  # Initialize an empty list for the song_queue
title_queue = []

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

options_string = f'{ffmpeg_options["before_options"]} -af volume={.05} {ffmpeg_options["options"]}'
 
class QueuedSong:
    def __init__(self, title, source):
        self.title = title
        self.source = source


@bot.command()
async def join(ctx):
    print("tried to join")
    voice_channel = ctx.author.voice.channel
    if voice_channel:
        await voice_channel.connect()
    else:
        await ctx.send("You're not in a voice channel.")


@bot.command()
async def radio(ctx, radio_name: str, volume: float = 0.08):
    global current_radio  # Access the global variable

    voice_client = ctx.voice_client
    voice_channel = ctx.author.voice.channel
    
    if voice_channel:
        if not voice_client:
            await voice_channel.connect()
            voice_client = ctx.voice_client
    else:
        await ctx.send("You are not in a voice channel.")
        return

    if radio_name.lower() in radio_sources:
        radio_url = radio_sources[radio_name.lower()]
        source = discord.FFmpegPCMAudio(radio_url, options=f"-af volume={volume}")
        voice_client.stop()
        voice_client.play(source)
        current_radio = radio_name.lower()  # Update the current radio
        
    else:
        await ctx.send("Invalid radio source.")


@bot.command()
async def play(ctx, *, search_query: str, volume: float = 0.35):
    voice_client = ctx.voice_client
    voice_channel = ctx.author.voice.channel
    
    if voice_channel:
        if not voice_client:
            await voice_channel.connect()
            voice_client = ctx.voice_client
    else:
        await ctx.send("You are not in a voice channel.")
        return
    
    if search_query.startswith(("http", "www", "youtube", "youtu.be")):
        video_url = search_query
    else:
        videosSearch = VideosSearch(search_query, limit=1)
        results = videosSearch.result()

        if results and 'result' in results and len(results['result']) > 0:
            video_url = results['result'][0]['link']
            print(video_url)
        else:
            await ctx.send("No search results found.")
            return

    yt = YouTube(video_url)
    stream = yt.streams.filter(only_audio=True).first()
    url2 = stream.url
    print("URL2:")
    print(url2)
    source = discord.FFmpegPCMAudio(url2, **ffmpeg_options)
    song_queue.append(source)
    queued_song = QueuedSong(yt.title, source)
    title_queue.append(queued_song)
    if voice_client.is_playing():
        await ctx.send("Added to the song_queue.")
    else:
        await play_next(ctx)


async def play_next(ctx):
    if song_queue:
        voice_client = ctx.voice_client
        source = song_queue.pop(0)
        title_queue.pop(0)
        voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))


@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client

    if song_queue and voice_client:
        next_source = song_queue.pop(0)
        voice_client.stop()
        voice_client.play(next_source)
        await ctx.send("Skipped!")
    elif not song_queue and voice_client:
        voice_client.stop()
        await ctx.send("Skipped! It's joever.")

@bot.command()
async def shuffle(ctx):
    global song_queue
    global title_queue
    
    paired_lists = list(zip(song_queue, title_queue))

    # Shuffle the pairs
    random.shuffle(paired_lists)

    # Unpack the shuffled pairs back into the original lists
    song_queue_tup, title_queue_tup = zip(*paired_lists)
    song_queue = list(song_queue_tup)
    title_queue = list(title_queue_tup)
    await ctx.send("Shuffled!")
    
    
@bot.command()
async def queue(ctx):
    if song_queue:
        song_queue_list = "\n".join([f"{index + 1}. {song.title}" for index, song in enumerate(title_queue)])
        await ctx.send(f"Current song_queue:\n{song_queue_list}")
    else:
        await ctx.send("The song_queue is empty.")


@bot.command()
async def remove(ctx, index: int):
    if 1 <= index < len(song_queue):
        song_queue.pop(index - 1)
        removed_song = title_queue.pop(index - 1)
        await ctx.send(f"Removed '{removed_song.title}' from the queue.")
    else:
        await ctx.send("Invalid index.")


@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()



bot_token = os.getenv("BOT_TOKEN")
# Use bot_token in your bot's run statement
bot.run(bot_token)
