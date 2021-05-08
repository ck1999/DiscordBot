import discord, json
from discord.ext import commands

async def open_json(name):
    with open(name, 'r') as f:
        return json.load(f)

async def save_data(array,name):
    with open(name, 'w') as f:
        json.dump(array, f)

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

class CookiesCount:

    def __init__(self, user, cookies):
        self.user = user
        self.cookies = cookies

    def __repr__(self):
        return f'<@{self.user}> с кол-вом {self.cookies} фисташек!'

class LeaderboardSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(self, ctx):
        id = ctx.guild.id
        users = await open_json('cogs/json_data/{}/users.json'.format(id))
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

def setup(bot):
    bot.add_cog(LeaderboardSystem(bot))