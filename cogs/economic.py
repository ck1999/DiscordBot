import discord, asyncio, typing, json, datetime
from discord.ext import commands

epoch = datetime.datetime.utcfromtimestamp(0)

async def open_json(name):
    with open(name, 'r') as f:
        return json.load(f)

async def save_data(array,name):
    with open(name, 'w') as f:
        json.dump(array, f)

async def update_data(users, user, id):
    if not f'{user.id}' in users:
        bank = await open_json('cogs/json_data/{}/bank.json'.format(id))
        users[f'{user.id}'] = {}
        users[f'{user.id}']['experience'] = 0
        users[f'{user.id}']['level'] = 1
        users[f'{user.id}']['cookies'] = 100
        users[f'{user.id}']['xp_time'] = (datetime.datetime.utcnow() - epoch).total_seconds()
        users[f'{user.id}']['gang_time'] = 0
        bank[f'{user.id}'] = {}
        bank[f'{user.id}']['amount'] = 0
        await save_data(bank, 'cogs/json_data/{}/bank.json'.format(id))

class BankSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fis(self, ctx):
        id = ctx.guild.id
        users = await open_json('cogs/json_data/{}/users.json'.format(id))

        await update_data(users, ctx.author, id)
        await ctx.reply('У тебя уже целых {} фисташек!'.format(users[f'{ctx.author.id}']['cookies']))

        await save_data(users, 'cogs/json_data/{}/users.json'.format(id))

    #Economic
    @commands.command()
    async def pay(self, ctx, member: discord.Member = None, amount: int = 10):
        guild_id = ctx.guild.id
        users = await open_json('cogs/json_data/{}/users.json'.format(guild_id))
        if not member or member.id == ctx.author.id:
            await ctx.send('Неверные реквезиты!')
        elif users[f'{ctx.author.id}']['cookies'] >= amount:
            id = member.id
            await update_data(users, member, guild_id)
            users[str(id)]['cookies'] += int(amount*(13/100))
            users[f'{ctx.author.id}']['cookies'] -= amount
            embed = discord.Embed(title='Чек', color=0xff5555)
            embed.add_field(name='**Сумма:**', value=amount, inline=False)
            embed.add_field(name='**Получатель:**', value=member.mention, inline=False)
            embed.add_field(name='**Налог:**', value=int(amount*(13/100)), inline=False)
            await ctx.reply(embed=embed)
            await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
        else:
            await ctx.reply('Сначала заработай нужное количество фисташек!')

    @commands.command()
    async def bank(self, ctx, amount: int = 0):
        id = ctx.guild.id
        users = await open_json('cogs/json_data/{}/users.json'.format(id))
        bank = await open_json('cogs/json_data/{}/bank.json'.format(id))
        if amount == 0:
            await update_data(users, ctx.author, id)
            embed = discord.Embed(title='Выписка из банка', color=0xff5555)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name='**В кармане:**', value=users[f'{ctx.author.id}']['cookies'], inline=True)
            embed.add_field(name='**В банке:**', value=bank[f'{ctx.author.id}']['amount'], inline=True)
            await ctx.reply(embed=embed)
        else:
            await update_data(users, ctx.author, id)
            bank[f'{ctx.author.id}']['amount'] += amount
            users[f'{ctx.author.id}']['cookies'] -= amount
            embed = discord.Embed(title='Чек', color=0xff5555)
            embed.add_field(name='**Сумма:**', value=amount, inline=False)
            embed.add_field(name='**Налог:**', value=0, inline=False)
            await ctx.reply(embed=embed)
        await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
        await save_data(bank, 'cogs/json_data/{}/bank.json'.format(id))

def setup(bot):
    bot.add_cog(BankSystem(bot))