import discord
from discord.ext import commands
from config import COOLDOWN_MEDIUM

class NotEnoughMoney(Exception):
    pass

class BankSystem(commands.Cog, name='Экономика'):
    
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        response = await self.bot.connector.get_data(f'guilds/{ctx.guild.id}', True)
        return response.get('setting_plugin_economy')

    @commands.command(aliases=['balance', 'bal'], description="Проверить количество фисташек на руках")
    @commands.cooldown(1, COOLDOWN_MEDIUM, commands.BucketType.user)
    @commands.guild_only()
    async def fis(self, ctx: commands.Context, member: discord.Member = None):
        user = member or ctx.message.author
        if user.bot:
            return await ctx.reply('Боты не играют в наши игры...')
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{user.id}')
        return await ctx.reply(f"У {user.mention} уже целых {response.get('balance')} фисташек!")

    @commands.command(aliases=['transfer'], description="Отправить фисташки другому пользователю")
    @commands.cooldown(1, COOLDOWN_MEDIUM, commands.BucketType.user)
    @commands.guild_only()
    async def pay(self, ctx: commands.Context, member: discord.Member = None, amount: int = 10):
        if member is None:
            return
        if member == ctx.author or member.bot:
            return await ctx.reply('А кому отправлять деньги? Непонятно...')
        if amount < 0:
            return await ctx.reply('Может тогда ты сам попросишь его отправить деньги?')
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{ctx.author.id}')
        __user_one_balance = response.get('balance') - amount
        if __user_one_balance < 0:
            return await ctx.reply('У тебя нет такой большой суммы денег...')
        context = {
                'balance': __user_one_balance,
            }
        await self.bot.connector.put_data(f'{ctx.guild.id}/{ctx.author.id}', data=context)
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{member.id}')
        __user_two_balance = response.get('balance') + int(amount*(87/100))
        context = {
                'balance': __user_two_balance,
            }
        await self.bot.connector.put_data(f'{ctx.guild.id}/{member.id}', data=context)
        embed = discord.Embed(title='Чек', color=0xff5555)
        embed.add_field(name='**Сумма:**', value=int(amount*(87/100)), inline=False)
        embed.add_field(name='**Получатель:**', value=member.mention, inline=False)
        embed.add_field(name='**Налог:**', value=amount-int(amount*(87/100)), inline=False)
        return await ctx.reply(embed=embed)

    @commands.command(aliases=['dep', 'put'], description="Положить деньги в банк")
    @commands.cooldown(1, COOLDOWN_MEDIUM, commands.BucketType.user)
    @commands.guild_only()
    async def deposit(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            return await ctx.reply('Хорошая попытка, но кредитный отдел в здании напротив!')
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{ctx.author.id}')
        if response.get('balance') < amount:
            return await ctx.reply('Извините меня, но у вас нет такой суммы на руках.')
        context = {
            'balance': response.get('balance') - amount,
            'bank': response.get('bank') + amount
        }
        await self.bot.connector.put_data(f'{ctx.guild.id}/{ctx.author.id}', data=context)
        embed = discord.Embed(title='Чек', color=0xff5555)
        embed.add_field(name='**Сумма:**', value=amount, inline=False)
        return await ctx.reply(embed=embed)

    @commands.command(aliases=['with','take'], description="Забрать деньги из банка")
    @commands.cooldown(1, COOLDOWN_MEDIUM, commands.BucketType.user)
    @commands.guild_only()
    async def withdraw(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            return await ctx.reply('Хорошая попытка ограбить банк, но увы...')
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{ctx.author.id}')
        if response.get('bank') < amount:
            return await ctx.reply('Извините меня, но у вас нет такой суммы на вашем банковском счёте.')
        context = {
            'balance': response.get('balance') + amount,
            'bank': response.get('bank') - amount
        }
        await self.bot.connector.put_data(f'{ctx.guild.id}/{ctx.author.id}', data=context)
        embed = discord.Embed(title='Чек', color=0xff5555)
        embed.add_field(name='**Сумма:**', value=amount, inline=False)
        return await ctx.reply(embed=embed)

    @commands.command(aliases=['ebal'], description="Посмотреть выписку из банка о счете")
    @commands.cooldown(1, COOLDOWN_MEDIUM, commands.BucketType.user)
    @commands.guild_only()
    async def bank(self, ctx: commands.Context):
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{ctx.author.id}')
        embed = discord.Embed(title='Выписка из банка', color=0x2C2F33)
        embed.add_field(name='**Банк**', value='```' + str(response.get('bank')) + '```', inline=True)
        embed.add_field(name='**Карман**', value='```' + str(response.get('balance')) + '```', inline=True)
        return await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(BankSystem(bot))