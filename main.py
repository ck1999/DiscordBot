import os, discord
from discord.ext import commands
from cogs.settings import settings
import requests

intents = discord.Intents(guilds=True, messages=True, members=True, voice_states=True, bans=True)

bot = commands.Bot(command_prefix=">", intents=intents)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(f'{filename[:-3]} loaded')

bot.run(settings['token'])