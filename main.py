import discord
from discord.ext import commands
from Token_get import getToken

bot = commands.Bot(command_prefix='!')


@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def test(ctx, arg):  # создаем асинхронную фунцию бота
    await ctx.send(arg)  # отправляем обратно аргумент

@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def cat(ctx, arg):  # создаем асинхронную фунцию бота
    await ctx.send('KITTY!')  # отправляем обратно аргумент

@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a + b)

import random

class Slapper(commands.Converter):
    async def convert(self, ctx, argument):
        to_slap = random.choice(ctx.guild.members)
        return '{0.author} slapped {1} because *{2}*'.format(ctx, to_slap, argument)

@bot.command()
async def slap(ctx, *, reason: Slapper):
    await ctx.send(reason)

@bot.command()
async def joined(ctx, *, member: discord.Member):
    await ctx.send('{0} joined on {0.joined_at}'.format(member))

import typing

@bot.command()
async def ban(ctx, members: commands.Greedy[discord.Member],
                   delete_days: typing.Optional[int] = 0, *,
                   reason: str):
    for member in members:
        await member.ban(delete_message_days=delete_days, reason=reason)

bot.run(getToken())
