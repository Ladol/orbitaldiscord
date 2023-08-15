import discord
from discord.ext import commands

# Define the intents your bot will use
intents = discord.Intents.default()
intents.voice_states = True
intents.messages = True  # Add this line to enable message content intent
intents.message_content = True

bot = commands.Bot(command_prefix=';', intents=intents)


@bot.command()
async def join(ctx):
    print("tried to join")
    voice_channel = ctx.author.voice.channel
    if voice_channel:
        await voice_channel.connect()
    else:
        await ctx.send("You're not in a voice channel.")

@bot.command()
async def play(ctx, volume: float = 0.05):
    print("tried to play")
    voice_client = ctx.voice_client

    if not voice_client:
        await ctx.invoke(bot.get_command('join'))

    source = discord.FFmpegPCMAudio("https://ec2.yesstreaming.net:3025/stream", options=f"-af volume={volume}")
    voice_client.play(source)

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()



bot.run("SECRET")
