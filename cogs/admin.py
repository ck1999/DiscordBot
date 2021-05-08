import discord, asyncio, typing
from discord.ext import commands

class NotAnAdmin(commands.CheckFailure):
    pass

class NoKickPerm(commands.CheckFailure):
    pass

class NoBanPerm(commands.CheckFailure):
    pass

def is_admin():
    async def predicate(ctx):
        for role in ctx.author.roles:
            if role.permissions.administrator:
                return True
        raise NotAnAdmin('Ты не админ!')
    return commands.check(predicate)

def can_kick():
    async def predicate(ctx):
        for role in ctx.author.roles:
            if role.permissions.administrator or role.permissions.kick_members:
                return True
        raise NoKickPerm('У тебя нет прав кикать пользователей!')
    return commands.check(predicate)

def can_ban():
    async def predicate(ctx):
        for role in ctx.author.roles:
            if role.permissions.administrator or role.permissions.ban_members:
                return True
        raise NoBanPerm('У тебя нет прав банить пользователей!')
    return commands.check(predicate)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @is_admin()
    async def test(self, ctx, arg):
        await ctx.reply('Working...')

    @commands.command()
    @can_ban()
    async def ban(self, ctx, members: commands.Greedy[discord.Member],
                    delete_days: typing.Optional[int] = 0, *,
                    reason: typing.Optional[str] = "No reason"):
        for member in members:
            await member.ban(delete_message_days=delete_days, reason=reason)
            await ctx.send('Покойся с миром, {0}'.format(member))

    @commands.command()
    @can_kick()
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason: str):
        for member in members:
            await member.kick(reason=reason)
            await ctx.send('Вышел и зашел нормально, {0}'.format(member))

    @commands.command()
    @is_admin()
    async def joined(self, ctx, *, member: discord.Member): 
        await ctx.send('{0} joined on {0.joined_at}'.format(member))

    @commands.command()
    @is_admin()
    async def userinfo(self, ctx: commands.Context, member: discord.Member):
        __id = member.id
        await ctx.send('**User found: **\n**ID:** {}\n**Username:** {}'.format(__id, member))
        await ctx.send('**Guild found: **\n**ID** {}'.format(ctx.guild.id))
        

def setup(bot):
    bot.add_cog(AdminCommands(bot))