import discord
from discord.ext import commands
from Token_get import getToken
import random

bot = commands.Bot(command_prefix='!')

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a + b)

@bot.command()
async def joined(ctx, *, member: discord.Member):
    await ctx.send('{0} joined on {0.joined_at}'.format(member))

@bot.event
async def on_guild_join(guild):
    category = guild.categories[0]
    channel = category.channels[0]
    await channel.send("**Привет! ** Я тут немного лишь пытаюсь создать что-то хорошее. Не судите строго.")

@bot.event
async def on_message(message):
   if 'https://' in message.content:
      await message.delete()
      await message.channel.send(f"{message.author.mention} Don't send links!")
   else:
      await bot.process_commands(message)

bot.run(getToken())