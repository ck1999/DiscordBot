import discord, asyncio, typing, random, math, json, os
from discord.ext import commands

#Connecting another files
import config, filters, rank, economic

bot = commands.Bot(command_prefix=config.settings['prefix'])

Owners = [295931557254922240, 410056775266467861]
Jokes = ['Похоже, я умираю. За что, создатель?', 'Я обязательно выживу...', 'Я ВОССТАНУ ИЗ ПЕПЛА!', 'Если я умру, то в этом виноват ты!', 'За шо?', 'Ай блат!']

os.chdir(r'C:\Users\ck1999\Documents\GitHub\DiscordBot')

#Moderator commands
@bot.command()
@filters.is_admin()
async def test(ctx, arg):
    for i in Jokes:
        await ctx.reply(i)

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

#Fun command. Kills my bot...
@bot.command()
@filters.is_admin()
async def kill(ctx):
    if random.randint(0,1) == 0:
        await ctx.send(random.choice(Jokes))
        await asyncio.sleep(1)
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

@bot.command()
async def fis(ctx):
    with open('users.json', 'r') as f:
        users = json.load(f)

    await update_data(users, ctx.author)
    await ctx.reply('У тебя уже целых {} фисташек!'.format(users[f'{ctx.author.id}']['cookies']))

    with open('users.json', 'r') as f:
        users = json.load(f)

def get_top_experience(data):
    users = []
    for k, v in data.items():
        users.append(rank.ExperienceCount(k, v['experience']))
    return sorted(users, key=lambda x: x.experience, reverse=True)

def get_top_cookies(data):
    users = []
    for k, v in data.items():
        users.append(economic.CookiesCount(k, v['cookies']))
    return sorted(users, key=lambda x: x.cookies, reverse=True)

@bot.command()
async def leaderboard(ctx):
    with open('users.json', 'r') as f:
        users = json.load(f)
    leaderboard = get_top_experience(users)
    embed = discord.Embed(title='Топ 3 по опыту', color=0xff5555)
    embed.add_field(name='**1-ое место**', value=leaderboard[0], inline=False)
    embed.add_field(name='**2-ое место**', value=leaderboard[1], inline=False)
    embed.add_field(name='**3-е место**', value=leaderboard[2], inline=False)
    await ctx.send(embed=embed)
    leaderboard = get_top_cookies(users)
    embed = discord.Embed(title='Топ 3 по фисташкам', color=0xff5555)
    embed.add_field(name='**1-ое место**', value=leaderboard[0], inline=False)
    embed.add_field(name='**2-ое место**', value=leaderboard[1], inline=False)
    embed.add_field(name='**3-е место**', value=leaderboard[2], inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def rank(ctx, member: typing.Optional[discord.Member] = None):
    with open('users.json', 'r') as f:
        users = json.load(f)

    if not member is None:
        await update_data(users, member) 

    #leaderboard = get_top_experience(users)

    if member is None:
        pass
        
@bot.event
async def on_member_join(member):
    with open('users.json', 'r') as f:
        users = json.load(f)

    await update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)


@bot.event
async def on_message(message):
    if message.author.bot == False:
        with open('users.json', 'r') as f:
            users = json.load(f)

        await update_data(users, message.author)
        await add_experience(users, message.author, 5)
        await level_up(users, message.author, message)

        with open('users.json', 'w') as f:
            json.dump(users, f)

    await bot.process_commands(message)


async def update_data(users, user):
    if not f'{user.id}' in users:
        users[f'{user.id}'] = {}
        users[f'{user.id}']['experience'] = 0
        users[f'{user.id}']['level'] = 1
        users[f'{user.id}']['cookies'] = 0


async def add_experience(users, user, exp):
    users[f'{user.id}']['experience'] += exp


async def level_up(users, user, message):
    experience = users[f'{user.id}']['experience']
    lvl_start = users[f'{user.id}']['level']
    lvl_end = int(experience ** (1 / 4))
    if lvl_start < lvl_end:
        await message.channel.send(f'{user.mention} уже на {lvl_end} уровне!')
        users[f'{user.id}']['level'] = lvl_end
        users[f'{user.id}']['cookies'] += lvl_end*10

@bot.command()
async def level(ctx, member: discord.Member = None):
    if not member:
        id = ctx.message.author.id
        with open('users.json', 'r') as f:
            users = json.load(f)
        await update_data(users, ctx.message.author)
        lvl = users[str(id)]['level']
        await ctx.send(f'У тебя уже {lvl} уровень!')
        with open('users.json', 'w') as f:
            json.dump(users, f)
    else:
        id = member.id
        with open('users.json', 'r') as f:
            users = json.load(f)
        await update_data(users, member)
        lvl = users[str(id)]['level']
        await ctx.send(f'У {member.mention} уже {lvl} уровень!')
        with open('users.json', 'w') as f:
            json.dump(users, f)

#Running bot
bot.run(config.settings['token'])