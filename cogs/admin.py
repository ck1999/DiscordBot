import discord, typing, json, datetime
from discord.ext import commands

class AdminCommands(commands.Cog, name='Модераторство'):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def test(self, ctx):
        embed = discord.Embed(title=f"Пользователь {ctx.author} покинул сервер", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=f'ID: {ctx.author.id}')
        await ctx.reply(embed=embed)

    @commands.command(description="Бан пользователя. Можно вводить несколько пользователей.\nЕсли нужно, то можно указать кол-во дней, за которые нужно удалить все сообщения и причину")
    @commands.has_permissions(ban_members=True, administrator=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member],
                    delete_days: typing.Optional[int] = 0, *,
                    reason: typing.Optional[str] = "No reason"):
        for member in members:
            await member.ban(delete_message_days=delete_days, reason=reason)
            await ctx.send('Покойся с миром, {0}'.format(member.mention))

    @commands.command(description="Кик пользователя. Можно вводить несколько пользователей.\nЕсли нужно, то можно указать причину")
    @commands.has_permissions(kick_members=True, administrator=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason: str):
        for member in members:
            await member.kick(reason=reason)
            await ctx.send('Вышел и зашел нормально, {0}'.format(member.mention))

    @commands.command(description="Дата, когда пользователь зашел на сервер")
    @commands.has_permissions(administrator=True)
    async def joined(self, ctx, *, member: discord.Member): 
        await ctx.send('{0} joined on {0.joined_at}'.format(member))

    @commands.command(hidden=True,description="Инфа об юзере + гильде")
    @commands.has_permissions(administrator=True)
    async def info(self, ctx: commands.Context, member: discord.Member):
        __id = member.id
        await ctx.send('**User found: **\n**ID:** {}\n**Username:** {}'.format(__id, member))
        await ctx.send('**Guild found: **\n**ID** {}'.format(ctx.guild.id))

    @commands.command(hidden=True, aliases=['set', 'log'],description="Сделать канал хранилищем логов")
    @commands.cooldown(5, 600, commands.BucketType.guild)
    async def set_log(self, ctx):
        if ctx.guild.owner:
            with open(f'cogs/json_data/{ctx.guild.id}/guild.json', 'r') as f:
                guild_info = json.load(f)
                guild_info["main"]['log'] = ctx.channel.id
            with open(f'cogs/json_data/{ctx.guild.id}/guild.json', 'w') as f:
                json.dump(guild_info, f)
            
def setup(bot):
    bot.add_cog(AdminCommands(bot))