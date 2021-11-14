import discord, typing, datetime, requests
from discord.ext import commands
from .settings import settings

class AdminCommands(commands.Cog, name='Модераторство'):
    def __init__(self, bot):
        self.bot = bot
    
    # @commands.command(hidden=True)
    # @commands.has_permissions(administrator=True)
    # @commands.guild_only()
    # async def test(self, ctx):
    #     request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
    #     await ctx.reply(f'**CONNECTION WITH SITE:** {request.status_code}')

    # @test.error
    # async def test_error(self, object, error):
    #     return await object.reply('**CONNECTION WITH SITE:** 404')

    @commands.command(description="Бан пользователя. Можно вводить несколько пользователей.\nЕсли нужно, то можно указать кол-во дней, за которые нужно удалить все сообщения и причину")
    @commands.has_permissions(ban_members=True, administrator=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], delete_days: typing.Optional[int] = 0, *, reason: typing.Optional[str] = "Без причины"):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_admin'):
            return
        if ctx.guild.system_channel is not None:
            log = ctx.guild.system_channel

        for member in members:
            await member.ban(delete_message_days=delete_days, reason=reason)
            embed = discord.Embed(title="Участника забанили", timestamp=datetime.datetime.utcnow())
            embed.add_field(name=f'Участник:', value=f'{member.mention}', inline=True)
            embed.add_field(name=f'Модератор:', value=f'{ctx.author.mention}', inline=True)
            embed.add_field(name=f'Причина:', value=f'{reason}', inline=True)
            embed.set_footer(text=f'ID: {member.id}')
            await log.send(embed=embed)

    @commands.command(description="Кик пользователя. Можно вводить несколько пользователей.\nЕсли нужно, то можно указать причину")
    @commands.has_permissions(kick_members=True, administrator=True)
    @commands.guild_only()
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason: typing.Optional[str] = "Без причины"):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_admin'):
            return
        if ctx.guild.system_channel is not None:
            log = ctx.guild.system_channel

        for member in members:
            await member.kick(reason=reason)
            embed = discord.Embed(title="Участника кикнули", timestamp=datetime.datetime.utcnow())
            embed.add_field(name=f'Участник:', value=f'{member.mention}', inline=True)
            embed.add_field(name=f'Модератор:', value=f'{ctx.author.mention}', inline=True)
            embed.add_field(name=f'Причина:', value=f'{reason}', inline=True)
            embed.set_footer(text=f'ID: {member.id}')
            await log.send(embed=embed)

    @commands.command(description="Дата, когда пользователь зашел на сервер")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_admin'):
            return

        await ctx.send(f'{member} зашел на сервер {member.joined_at}')

    @commands.command(hidden=True,description="Инфа об юзере + гильде")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def info(self, ctx: commands.Context, member: discord.Member):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_admin'):
            return

        await ctx.send(f'**Юзер найден: **\n**ID:** {member.id}\n**Никнейм:** {member.mention}')
        await ctx.send(f'**Сервер найден: **\n**ID** {ctx.guild.id}')

    @commands.command(hidden=True, aliases=['set', 'log'],description="Сделать канал хранилищем логов *")
    @commands.cooldown(5, 600, commands.BucketType.guild)
    @commands.guild_only()
    async def set_log(self, ctx):
        if ctx.guild.owner:
            pass

    @commands.command(description="Очистка чата. AXTUNG! Работает оооочень медленно, зато с плюшками!\nПример команды: /clear 300 @ck1999")
    @commands.cooldown(5, settings.get('cooldown_large'), commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def clear(self, ctx, number: int, user: discord.Member = None):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if request.json().get('setting_plugin_admin'):
            msg = await ctx.channel.history(limit=number).flatten()
            count = 0
            if user is not None:
                for i in msg:
                    if i.author == user:
                        await i.delete()
                        count += 1
            else:
                for i in msg:
                    await i.delete()
                    count += 1
            await ctx.reply(f'Завершено. Удалено {count} сообщений!')

def setup(bot):
    bot.add_cog(AdminCommands(bot))