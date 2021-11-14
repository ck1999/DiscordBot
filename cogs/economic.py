import discord, requests
from discord.ext import commands
from .settings import settings

class NotEnoughMoney(Exception):
    pass

class BankSystem(commands.Cog, name='Экономика'):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['balance', 'bal'], description="Проверить количество фисташек на руках")
    @commands.cooldown(1, settings.get('cooldown_medium'), commands.BucketType.user)
    @commands.guild_only()
    async def fis(self, ctx: commands.Context, member: discord.Member = None):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_economy'):
            return
        user = member or ctx.message.author
        if user.bot:
            return await ctx.reply('Боты не играют в наши игры...')
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{user.id}')
        return await ctx.reply('У {} уже целых {} фисташек!'.format(user.mention, request.json()['balance']))

    @commands.command(aliases=['transfer'], description="Отправить фисташки другому пользователю\nПример команды: !pay @ck1999 10")
    @commands.cooldown(1, settings.get('cooldown_medium'), commands.BucketType.user)
    @commands.guild_only()
    async def pay(self, ctx: commands.Context, member: discord.Member = None, amount: int = 10):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_economy'):
            return
        if member is None:
            return
        if member == ctx.author or member.bot:
            return await ctx.reply('А кому отправлять деньги? Непонятно...')
        if amount < 0:
            return await ctx.reply('Может тогда ты сам попросишь его отправить деньги?')
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}')
        __user_one_balance = request.json().get('balance') - amount
        if __user_one_balance < 0:
            return await ctx.reply('У тебя нет такой большой суммы денег...')
        context = {
                'balance': __user_one_balance,
            }
        requests.put(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}', data=context)
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{member.id}')
        __user_two_balance = request.json().get('balance') + int(amount*(87/100))
        context = {
                'balance': __user_two_balance,
            }
        request = requests.put(settings.get('api')+f'{ctx.guild.id}/{member.id}', data=context)
        embed = discord.Embed(title='Чек', color=0xff5555)
        embed.add_field(name='**Сумма:**', value=int(amount*(87/100)), inline=False)
        embed.add_field(name='**Получатель:**', value=member.mention, inline=False)
        embed.add_field(name='**Налог:**', value=amount-int(amount*(87/100)), inline=False)
        return await ctx.reply(embed=embed)

    @commands.command(aliases=['dep', 'put'], description="Положить деньги в банк\nПример команды: !dep 10")
    @commands.cooldown(1, settings.get('cooldown_medium'), commands.BucketType.user)
    @commands.guild_only()
    async def deposit(self, ctx: commands.Context, amount: int):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json()['setting_plugin_economy']:
            return
        if amount <= 0:
            return await ctx.reply('Хорошая попытка, но кредитный отдел в здании напротив!')
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}')
        if request.json().get('balance') < amount:
            return await ctx.reply('Извините меня, но у вас нет такой суммы на руках.')
        context = {
            'balance': request.json().get('balance') - amount,
            'bank': request.json().get('bank') + amount
        }
        requests.put(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}', data=context)
        embed = discord.Embed(title='Чек', color=0xff5555)
        embed.add_field(name='**Сумма:**', value=amount, inline=False)
        return await ctx.reply(embed=embed)

    @commands.command(aliases=['with','take'], description="Забрать деньги из банка\nПример команды: !take 10")
    @commands.cooldown(1, settings.get('cooldown_medium'), commands.BucketType.user)
    @commands.guild_only()
    async def withdraw(self, ctx: commands.Context, amount: int):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_economy'):
            return
        if amount <= 0:
            return await ctx.reply('Хорошая попытка ограбить банк, но увы...')
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}')
        if request.json().get('bank') < amount:
            return await ctx.reply('Извините меня, но у вас нет такой суммы на вашем банковском счёте.')
        context = {
            'balance': request.json().get('balance') + amount,
            'bank': request.json().get('bank') - amount
        }
        requests.put(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}', data=context)
        embed = discord.Embed(title='Чек', color=0xff5555)
        embed.add_field(name='**Сумма:**', value=amount, inline=False)
        return await ctx.reply(embed=embed)

    @commands.command(aliases=['ebal'], description="Посмотреть выписку из банка о счете")
    @commands.cooldown(1, settings.get('cooldown_medium'), commands.BucketType.user)
    @commands.guild_only()
    async def bank(self, ctx: commands.Context):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_economy'):
            return
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}')
        embed = discord.Embed(title='Выписка из банка', color=0x2C2F33)
        embed.add_field(name='**Банк**', value='```' + str(request.json().get('bank')) + '```', inline=True)
        embed.add_field(name='**Карман**', value='```' + str(request.json().get('balance')) + '```', inline=True)
        return await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(BankSystem(bot))