import discord, requests
from discord.ext import commands
from .settings import settings

def get_top_experience(data):
    users = []
    for i in data:
        users.append(ExperienceCount(i['user'], i['exp']))
    return sorted(users, key=lambda x: x.experience, reverse=True)

def get_top_cookies(data):
    users = []
    for i in data:
        users.append(CookiesCount(i['user'], i['balance']+i['bank']))
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
    @commands.cooldown(1, settings.get('cooldown_large'), commands.BucketType.user)
    @commands.guild_only()
    async def leaderboard(self, ctx):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_rank'):
            return
        request = requests.get(settings.get('api')+f'{ctx.guild.id}')
        users = request.json()
        leaderboard = get_top_experience(users)
        embed = discord.Embed(title='Топ по опыту', color=0xff5555)
        for i in range(len(leaderboard[:5])):
            embed.add_field(name=f'**{i+1} место**', value=leaderboard[i], inline=False)
        await ctx.send(embed=embed)
        leaderboard = get_top_cookies(users)
        embed = discord.Embed(title='Топ по фисташкам', color=0xff5555)
        for i in range(len(leaderboard[:5])):
            embed.add_field(name=f'**{i+1} место**', value=leaderboard[i], inline=False)
        await ctx.send(embed=embed)

    @commands.command(description="Место в таблице лидеров по опыту")
    @commands.cooldown(1, settings.get('cooldown_large'), commands.BucketType.user)
    @commands.guild_only()
    async def rank(self, ctx, member: discord.Member = None):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_rank'):
            return
        request = requests.get(settings.get('api')+f'{ctx.guild.id}')
        users = request.json()
        user = member or ctx.author
        leaderboard = get_top_experience(users)
        for k in range(len(leaderboard)):
            if leaderboard[k].get_user() == str(user.id):
                await ctx.reply(f'{user.mention} занимает {k+1} по опыту!')
        leaderboard = get_top_cookies(users)
        for k in range(len(leaderboard)):
            if leaderboard[k].get_user() == str(user.id):
                await ctx.reply(f'{user.mention} занимает {k+1} по фисташкам!')


def setup(bot):
    bot.add_cog(LeaderboardSystem(bot))