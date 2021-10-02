import asyncio
from hosting import keep_alive
import os
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
import random
from pathlib import (
    Path,
)

from random import choice

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
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
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
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def is_connected(ctx):
    voice_client = ctx.message.guild.voice_client
    return voice_client and voice_client.is_connected()


client = commands.Bot(command_prefix='?')
media_folder = Path(
    __file__, "../media"
).resolve()

status = ['dumbest ', 'dumbest bot since 1969', 'my owner has evaded taxes']
queue = []
loop = False


def get_image(ctx):
    images = list(media_folder.glob(f"{ctx.command}/*"))
    return discord.File(random.choice(images))


@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}!  you a retard? See `?help` command for details!')


# This command returns the latency

@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**bing!** Latency: {round(client.latency * 1000)}ms')


# This command returns a random welcome message

@client.command(name='hello', help='This command returns a random welcome message')
async def hello(ctx):
    responses = ['i havent been paid', ' retard', 'my owner has kept me hostage in his basement', 'Hi', 'let me sleep']
    await ctx.send(choice(responses))


# this command randomly sends insults

@client.command(name='die', help='This command returns a random last words')
async def die(ctx):
    responses = ['im immortal ', 'im immortal moron', 'you really thought you could do that?']
    await ctx.send(choice(responses))


@client.command(name="spray", aliases=["spritzered"])
async def spray(ctx):
    responses = ['https://i.imgur.com/jz88lOz.jpeg', 'https://i.imgur.com/roIcGSR.gif']
    await ctx.send(choice(responses))


@client.command(name="bonk")
async def bonk(ctx):
    responses = ['https://i.imgur.com/SYBhFrU.gif', 'https://i.imgur.com/ElNAAwa.gif']
    await ctx.send(choice(responses))


# who made the bot?

@client.command(name='whodid', help='This command returns the credits')
async def whodid(ctx):
    await ctx.send('Made by `murt`')
    await ctx.send('Thanks to `murts brain` for coming up with the idea')
    await ctx.send(
        'Thanks to `murts big brain gigachad grindset` for helping with the `?die` and `?whoreallydid` command')


# credits commands


@client.command(name='whoreallydid', help='This command returns the TRUE credits')
async def whoreallydid(ctx):
    responses = ['**200 Social Credit added**', 'dQw4w9WgXcQ', 'bruh moment', '**1000000 Social creddit added**',
                 '**all social credit removed**']
    await ctx.send(choice(responses))


@client.command(name='loop', help='This command toggles loop mode')
async def loop_(ctx):
    global loop

    if loop:
        await ctx.send('Loop mode is now `False!`')
        loop = False

    else:
        await ctx.send('Loop mode is now `True!`')
        loop = True


@client.command(name='join', help='This command makes the bot join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("y u no connect to vc")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()


@client.command(name='play', help='This command plays songs')
async def play(ctx):
    global queue

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))
    del (queue[0])


@client.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    server = ctx.message.guild

    voice_channel = server.voice_client

    voice_channel.pause()


@client.command(name='resume', help='This command resumes the song!')
async def resume(ctx):
    server = ctx.message.guild

    voice_channel = server.voice_client

    voice_channel.resume()


@client.command(name='cancel', help='This command stops the song!')
async def cancel(ctx):
    server = ctx.message.guild

    voice_channel = server.voice_client

    voice_channel.cancel()


@client.command(name='queue', help='This command adds a song to the queue')
async def queue_(ctx, url):
    global queue

    queue.append(url)
    await ctx.send(f'`{url}` added to queue!')


@client.command(name='remove', help='This command removes an item from the list')
async def remove(ctx, number):
    global queue

    try:
        del (queue[int(number)])
        await ctx.send(f'Your queue is now `{queue}!`')

    except:
        await ctx.send('Your queue is either **empty** or the index is **out of range**')


@client.command(name='view', help='This command shows the queue')
async def view(ctx):
    await ctx.send(f'Your queue is now `{queue}!`')


@client.command(name='stop', help='This command stops the music and makes the bot leave the voice channel')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()


@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


keep_alive()
token = os.environ.get("ODkzNDQ1NDcwNjUzOTE1MTQ3.YVbj7w.MG4PdzmnMXAprwuY6e0gIIYnkPA")
client.run('ODkzNDQ1NDcwNjUzOTE1MTQ3.YVbj7w.MG4PdzmnMXAprwuY6e0gIIYnkPA')
