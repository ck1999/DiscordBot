import discord, json
from discord import player
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
        if filename == 'bank':
            array[f'{user.id}']['amount'] = 0
    await save_data(array, path)
  
class BankSystem(commands.Cog, name='Экономика'):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(enabled=False)
    @commands.guild_only()
    async def fis(self, ctx, member: discord.Member = None):
        id = ctx.guild.id
        path = 'cogs/json_data/{}/users.json'.format(id)
        user = member or ctx.message.author
        users = await open_json(path)
        await ctx.reply('У {} уже целых {} фисташек!'.format(user.mention, users[f'{user.id}']['cookies']))

    @commands.command(description="Отправить фисташки другому пользователю\nПример команды: !pay @ck1999 10")
    @commands.guild_only()
    async def pay(self, ctx, member: discord.Member = None, amount: int = 10):
        guild_id = ctx.guild.id
        path = 'cogs/json_data/{}/users.json'.format(guild_id)
        user = member
        if member == ctx.author or member.bot:
            raise commands.MemberNotFound
        id = user.id
        users = await open_json(path)
        users[str(id)]['cookies'] += int(amount*(87/100))
        users[f'{ctx.author.id}']['cookies'] -= amount
        embed = discord.Embed(title='Чек', color=0xff5555)
        embed.add_field(name='**Сумма:**', value=int(amount*(87/100)), inline=False)
        embed.add_field(name='**Получатель:**', value=user.mention, inline=False)
        embed.add_field(name='**Налог:**', value=amount-int(amount*(87/100)), inline=False)
        await ctx.reply(embed=embed)
        await save_data(users, path)

    @pay.error
    async def pay_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.reply('Укажи пользователя, которому хочешь перевести свои фисташки!')

    @commands.command(aliases=['dep', 'put'],description="Положить деньги в банк\nПример команды: !dep 10")
    @commands.guild_only()
    async def deposit(self, ctx, amount: int):
        id = ctx.guild.id
        path_users = 'cogs/json_data/{}/users.json'.format(id)
        path_bank = 'cogs/json_data/{}/bank.json'.format(id)
        user = ctx.author
        await update_data('bank', user, id)
        users = await open_json(path_users)
        bank = await open_json(path_bank)
        if users[f'{user.id}']['cookies'] - amount >= 0:
            bank[f'{user.id}']['amount'] += amount
            users[f'{user.id}']['cookies'] -= amount 
            embed = discord.Embed(title='Чек', color=0xff5555)
            embed.add_field(name='**Сумма:**', value=amount, inline=False)
            embed.add_field(name='**Налог:**', value=0, inline=False) 
            await ctx.reply(embed=embed)
        await save_data(users, path_users)
        await save_data(bank, path_bank)

    @commands.command(aliases=['with','take'],description="Забрать деньги из банка\nПример команды: !take 10")
    @commands.guild_only()
    async def withdraw(self, ctx, amount: int):
        id = ctx.guild.id
        path_users = 'cogs/json_data/{}/users.json'.format(id)
        path_bank = 'cogs/json_data/{}/bank.json'.format(id)
        user = ctx.author
        await update_data('bank', user, id)
        users = await open_json(path_users)
        bank = await open_json(path_bank)
        if bank[f'{user.id}']['amount'] - amount >= 0:
            bank[f'{user.id}']['amount'] -= amount
            users[f'{user.id}']['cookies'] += amount 
            embed = discord.Embed(title='Чек', color=0xff5555)
            embed.add_field(name='**Сумма:**', value=amount, inline=False)
            embed.add_field(name='**Налог:**', value=0, inline=False) 
            await ctx.reply(embed=embed)
        await save_data(users, path_users)
        await save_data(bank, path_bank)

    @commands.command(aliases=['bal','balance','ebal'],description="Посмотреть выписку из банка о счете")
    @commands.guild_only()
    async def bank(self, ctx):
        id = ctx.guild.id
        path_users = 'cogs/json_data/{}/users.json'.format(id)
        path_bank = 'cogs/json_data/{}/bank.json'.format(id)
        user = ctx.author
        await update_data('bank', user, id)
        users = await open_json(path_users)
        bank = await open_json(path_bank)
        embed = discord.Embed(title='Выписка из банка', color=0xff5555)
        embed.set_footer(text=user.name, icon_url=user.avatar_url)
        embed.add_field(name='**В банке:**', value=bank[f'{user.id}']['amount'])
        embed.add_field(name='**В кармане:**', value=users[f'{user.id}']['cookies'], inline=False)
        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(BankSystem(bot))