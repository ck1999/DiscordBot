import discord, asyncio, random, os, json
from discord.ext import commands

import config

bot = commands.Bot(command_prefix="!")

Owners = [295931557254922240, 410056775266467861]

Jokes = ['Похоже, я умираю. За что, создатель?', 'Я обязательно выживу...', 'Я ВОССТАНУ ИЗ ПЕПЛА!', 'Если я умру, то в этом виноват ты!', 'За шо?', 'Ай блат!']

@bot.command()
@commands.is_owner()
async def kill(ctx):
    await ctx.send(random.choice(Jokes))
    await asyncio.sleep(1)
    await bot.close()

@bot.command(name='load')
@commands.is_owner()
async def load_coag(ctx, name):
    bot.load_extension(f'cogs.{name}')

@bot.command(name='unload')
@commands.is_owner()
async def unload_coag(ctx, name):
    bot.unload_extension(f'cogs.{name}')

@bot.command(name='reload')
@commands.is_owner()
async def reload_coag(ctx, name):
    bot.unload_extension(f'cogs.{name}')
    bot.load_extension(f'cogs.{name}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_guild_join(guild):
    os.chdir('cogs/json_data/')
    os.mkdir('{}'.format(guild.id))
    os.chdir('{}'.format(guild.id))
    with open('users.json', mode='w') as f:
        json.dump({}, f)
    with open('bank.json', mode='w') as f:
        json.dump({}, f)
    with open('ruletka.json', mode='w') as f:
        json.dump({"ruletka": {"total": 0}}, f)
    with open('dice.json', mode='w') as f:
        json.dump({}, f)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Переписывается код...'))

bot.run(config.settings['token'])