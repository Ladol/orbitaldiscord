import discord
from discord.ext import commands
import youtube_dl
import random

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

@bot.command()
async def join(ctx):
    print("tried to join")
    voice_channel = ctx.author.voice.channel
    if voice_channel:
        await voice_channel.connect()
    else:
        await ctx.send("You're not in a voice channel.")


@bot.command()
async def play(ctx, radio_name: str, volume: float = 0.05):
    global current_radio  # Access the global variable

    voice_client = ctx.voice_client
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    #https://youtube.com/playlist?list=PLpd3Tq-TObdr_HLYQonoZ3i6HlJUe8tn6

    if radio_name.lower() in radio_sources:
        radio_url = radio_sources[radio_name.lower()]
        source = discord.FFmpegPCMAudio(radio_url, options=f"-af volume={volume}")
        voice_client.stop()  # Stop the currently playing audio
        voice_client.play(source)
        current_radio = radio_name.lower()  # Update the current radio
    elif 'youtube' in radio_name:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(radio_name, download=False)
            if 'entries' in info_dict:
                playlist_entries = info_dict['entries']
                random.shuffle(playlist_entries)
                for entry in playlist_entries:
                    source = discord.FFmpegPCMAudio(entry['url'], options=f"-af volume={volume}")
                    voice_client.stop()  # Stop the currently playing audio
                    voice_client.play(source)
                    while voice_client.is_playing():
                        await asyncio.sleep(1)  # Wait until the current song finishes
            else:
                await ctx.send("No playlist entries found.")
    else:
        await ctx.send("Invalid radio source.")


@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()



bot_token = os.getenv("BOT_TOKEN")
# Use bot_token in your bot's run statement
bot.run(bot_token)
