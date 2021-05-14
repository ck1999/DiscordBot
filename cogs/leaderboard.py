import discord, json, datetime
from discord.ext import commands

async def open_json(name):
    with open(name, 'r') as f:
        return json.load(f)

async def save_data(array,name):
    with open(name, 'w') as f:
        json.dump(array, f)

async def update_data(filename, user, id):
    path = 'cogs/json_data/{}/{}.json'.format(id,filename)
    array = await open_json(path)
    if not f'{user.id}' in array:
        array[f'{user.id}'] = {}
    await save_data(array, path)

def get_top_experience(data):
    users = []
    for k, v in data.items():
        users.append(ExperienceCount(k, v['experience']))
    return sorted(users, key=lambda x: x.experience, reverse=True)

def get_top_cookies(data):
    users = []
    for k, v in data.items():
        users.append(CookiesCount(k, v['cookies']))
    return sorted(users, key=lambda x: x.cookies, reverse=True)

class ExperienceCount:

    def __init__(self, user, experience):
        self.user = user
        self.experience = experience

    def __repr__(self):
        return f'<@{self.user}> с {self.experience} очками опыта'

    def get_user(self):
        return self.user

class CookiesCount:

    def __init__(self, user, cookies):
        self.user = user
        self.cookies = cookies

    def __repr__(self):
        return f'<@{self.user}> с кол-вом {self.cookies} фисташек!'
    
    def get_user(self):
        return self.user

class LeaderboardSystem(commands.Cog, name='Система уровней'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Топ района по опыту и фисташкам")
    @commands.guild_only()
    async def leaderboard(self, ctx):
        if ctx.guild.member_count < 5:
            await ctx.reply('Маловато у тебя пацанов на районе...')
            return 0
        id = ctx.guild.id
        path = 'cogs/json_data/{}/users.json'.format(id)
        users = await open_json(path)
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

    @commands.command(description="Место в таблице лидеров по опыту")
    @commands.guild_only()
    async def rank(self, ctx, member: discord.Member = None):
        id = ctx.guild.id
        user = member or ctx.author
        path = 'cogs/json_data/{}/users.json'.format(id)
        users = await open_json(path)
        leaderboard = get_top_experience(users)
        for k in range(len(leaderboard)):
            if leaderboard[k].get_user() == str(user.id):
                await ctx.reply(f'Ты занимаешь {k+1} место!')


def setup(bot):
    bot.add_cog(LeaderboardSystem(bot))