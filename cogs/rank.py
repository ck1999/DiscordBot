import discord, asyncio, typing, json, time
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

async def count_user_experience(message, amount, id):
    path = 'cogs/json_data/{}/users.json'.format(id)
    array = await open_json(path)
    user = message.author
    time_diff = time.time() - array[f'{user.id}']['XP_TIME_LOCK']
    if time_diff >= 3:
        array[f'{user.id}']['experience'] += amount
        array[f'{user.id}']['XP_TIME_LOCK'] = time.time()
        level_start = array[f'{user.id}']['level']
        level_end = int(array[f'{user.id}']['experience'] ** (1 / 4))
        if level_start < level_end:
            await message.channel.send(f'{user.mention} уже на {level_end} уровне!')
            array[f'{user.id}']['level'] = level_end
            array[f'{user.id}']['cookies'] += level_end*10
    await save_data(array, path)

class Birthday(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def set_birthday(self, ctx, date, member: discord.Member = None):
        id = ctx.guild.id
        birthday_date = await open_json('cogs/json_data/{}/birthday.json'.format(id))
        
        date = date.split('-')
        for i in range(len(date)):
            date[i] = int(date[i])

        if member == None:
            if len(date) == 2:
                birthday_date[f'{ctx.author.id}']['birthday_month'] = date[0]
                birthday_date[f'{ctx.author.id}']['birthday_day'] = date[1]
            elif len(date) == 3:
                birthday_date[f'{ctx.author.id}']['birthday_year'] = date[0]
                birthday_date[f'{ctx.author.id}']['birthday_month'] = date[1]
                birthday_date[f'{ctx.author.id}']['birthday_day'] = date[2]
        else:
            if len(date) == 2:
                birthday_date[f'{member.id}']['birthday_month'] = date[0]
                birthday_date[f'{member.id}']['birthday_day'] = date[1]
            elif len(date) == 3:
                birthday_date[f'{member.id}']['birthday_year'] = date[0]
                birthday_date[f'{member.id}']['birthday_month'] = date[1]
                birthday_date[f'{member.id}']['birthday_day'] = date[2]
        await save_data(birthday_date, 'cogs/json_data/{}/birthday.json'.format(id))
            
    @commands.command()
    async def birthday(self, ctx, member: discord.Member = None):
        id = ctx.guild.id
        users = await open_json('cogs/json_data/{}/users.json'.format(id))
        bank = await open_json('cogs/json_data/{}/bank.json'.format(id))

        await update_data(bank, users, ctx.author)

        if member == None:
            if users[f'{ctx.author.id}']['birthday_day'] == 0:
                await ctx.reply('Я не знаю когда был рожден такой цветок жизни!')
            elif users[f'{ctx.author.id}']['birthday_year'] == 1:
                await ctx.reply('Хм. Ты был рожден {}.{}'.format(users[f'{ctx.author.id}']['birthday_day'],users[f'{ctx.author.id}']['birthday_month']))
            else:
                await ctx.reply('Ты был рожден {}.{}.{}'.format(users[f'{ctx.author.id}']['birthday_day'],users[f'{ctx.author.id}']['birthday_month'], users[f'{ctx.author.id}']['birthday_year']))
        else:
            await update_data(bank, users, member)
            if users[f'{member.id}']['birthday_day'] == 0:
                await ctx.reply('Я не знаю когда был рожден такой цветок жизни!')
            elif users[f'{member.id}']['birthday_year'] == 1:
                await ctx.reply('Хм. Он был рожден в {}.{}'.format(users[f'{member.id}']['birthday_day'],users[f'{member.id}']['birthday_month']))
            else:
                await ctx.reply('Он был рожден {}.{}.{}'.format(users[f'{member.id}']['birthday_day'],users[f'{member.id}']['birthday_month'],users[f'{member.id}']['birthday_year']))
        await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
        await save_data(bank, 'cogs/json_data/{}/bank.json'.format(id))

class RankSystem(commands.Cog, name='Уровни'):

    def __init__(self, bot):
        self.bot = bot
            
    @commands.Cog.listener()
    async def on_member_join(self, member):
        id = member.guild.id
        await update_data('users', member, id)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            id = message.guild.id
        except AttributeError:
            return 0
        if not message.author.bot:
            await count_user_experience(message, 5, id)

    @commands.command(description="Информация об уровне\nПримеры команд:\n!level\n!level @ck1999")
    @commands.guild_only()
    async def level(self, ctx, member: discord.Member = None):
        guild_id = ctx.guild.id
        path = 'cogs/json_data/{}/users.json'.format(guild_id)
        user = member or ctx.message.author
        id = user.id
        users = await open_json(path)
        await ctx.send('У {} уже {} уровень!'.format(user.mention, users[str(id)]['level']))

def setup(bot):
    bot.add_cog(RankSystem(bot))
    #bot.add_cog(Birthday(bot))