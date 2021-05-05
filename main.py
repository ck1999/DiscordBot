import discord, asyncio, typing, random
from discord.ext import commands

#Connecting another files
import config, filters

bot = commands.Bot(command_prefix=config.settings['prefix'], description="Я просто играюсь в песке...")

Owners = [295931557254922240, 410056775266467861]
Jokes = ['Похоже, я умираю. За что, создатель?', 'Я обязательно выживу...', 'Я ВОССТАНУ ИЗ ПЕПЛА!', 'Если я умру, то в этом виноват ты!']

#Users level list
Users = [[295931557254922240, 2]]

#Admin commands

async def Tomb(ctx, count):
    if count != 0:
        await ctx.send("**{}**".format(count))
        await asyncio.sleep(1)
        await Tomb(ctx, count-1)

@bot.command()
@filters.is_admin()
async def test(ctx, arg):
    await ctx.reply(arg)
    await ctx.reply(ctx.author.roles)

@bot.command()
@filters.can_ban()
async def ban(ctx, members: commands.Greedy[discord.Member],
                   delete_days: typing.Optional[int] = 0, *,
                   reason: typing.Optional[str] = "No reason"):
    for member in members:
        await member.ban(delete_message_days=delete_days, reason=reason)
        await ctx.send('Покойся с миром, {0}'.format(member))

@bot.command()
@filters.can_kick()
async def kick(ctx, members: commands.Greedy[discord.Member], *, reason: str):
    for member in members:
        await member.kick(reason=reason)
        await ctx.send('Вышел и зашел нормально, {0}'.format(member))

@bot.command()
@filters.is_admin()
async def joined(ctx, *, member: discord.Member): 
    await ctx.send('{0} joined on {0.joined_at}'.format(member))

@bot.command()
@filters.is_admin()
async def userinfo(ctx: commands.Context, member: discord.Member):
    __id = member.id
    await ctx.send('**User found: **\n**ID:** {}\n**Username:** {}'.format(__id, member))

@bot.command()
@filters.is_admin()
async def kill(ctx):
    if random.randint(0,1) == 0:
        await ctx.send(random.choice(Jokes))
        await asyncio.sleep(1)
        await bot.close()
    else: 
        await ctx.send('**~_~_~_~_~_~_   Запускаю самоуничтожение через:   _~_~_~_~_~_~**')
        await Tomb(ctx, 10)
        await ctx.send('**~_~_~_~_~_~_   Ошибка запуска _~_~_~_~_~_~**')
        await bot.close()

#Errors

@ban.error
async def ban_errors(ctx, error):
    if isinstance(error, filters.NoBanPerm):
        await ctx.reply(error)

@kick.error
async def kick_errors(ctx, error):
    if isinstance(error, filters.NoKickPerm):
        await ctx.reply(error)

@test.error
async def test_error(ctx, error):
    if isinstance(error, filters.NotAnAdmin):
        await ctx.reply(error)

#Running bot

bot.run(config.settings['token'])