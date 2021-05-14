import discord, asyncio, typing, json, random
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

async def ruletka_start(rr, ctx, bot, rr_path):
        await ctx.send('Да начнется игра!')
        rr.pop('total')
        players = []
        id = ctx.guild.id
        path = 'cogs/json_data/{}/users.json'.format(id)
        users = await open_json(path)

        for k in rr:
            players.append(k)

        while len(players) > 1:
            await ctx.send('Я заряжаю патрон и...')
            user_id = random.choices(players)
            players.remove(f'{user_id[0]}')
            user = await bot.fetch_user(f'{user_id[0]}')
            await ctx.send(f'Убиваю {user.mention}!')
            await asyncio.sleep(5)


        user = await bot.fetch_user('{}'.format(players[0]))
        await ctx.send('Похоже, что остался только {}'.format(user.mention))
        await ctx.send('Поздравляю тебя с победой!')
        users[f'{user.id}']['cookies'] += rr['ruletka']['total']
        rr['ruletka']['total'] = 0
        rr['ruletka'].pop(f'{user.id}', None)

        await save_data(users, path)
        await save_data(rr, rr_path)

class GamesSystem(commands.Cog, name='Игры'):

    def __init__(self, bot):
        self.bot = bot
        self.barmen = None

    @commands.command(description="Сыграть с другими пользователями в русскую рулетку. Можно на деньги\nНапример:\n/ruletka\n/ruletka 50")
    @commands.guild_only()
    async def ruletka(self, ctx, price: typing.Optional[int] = 0):
        
        id = ctx.guild.id
        path = 'cogs/json_data/{}/users.json'.format(id)
        users = await open_json(path)
        user = ctx.author
        path_rr = 'cogs/json_data/{}/ruletka.json'.format(id)
        rr = await open_json(path_rr)

        if f'{user.id}' in rr['ruletka']:
            users[f'{user.id}']['cookies'] += rr['ruletka'][f'{user.id}']
            rr['ruletka']['total'] -= rr['ruletka'][f'{user.id}']
            rr['ruletka'].pop(f'{user.id}', None)
            await ctx.reply('Уже уходишь? Жаль...')
            await save_data(users, path)
            await save_data(rr, path_rr)
            return 0
        
        if users[f'{ctx.author.id}']['cookies'] - price < 0:
            await ctx.reply('У тебя недостаточно фисташек!')
            return 0
        
        rr['ruletka'][f'{ctx.author.id}'] = price
        users[f'{ctx.author.id}']['cookies'] -= price
        rr['ruletka']['total'] += price
        await ctx.reply('Теперь ты в игре, смертный!')
        
        await save_data(users, path)
        await save_data(rr, path_rr)

    @commands.command(description="Запускает игру в русскую рулетку. \nНужно как минимум 3 участника\nПодробнее в !help ruletka")
    @commands.guild_only()
    async def start(self, ctx):
        id = ctx.guild.id
        path = 'cogs/json_data/{}/ruletka.json'.format(id)
        persons = await open_json(path)
        if not persons['ruletka'][f'{ctx.author.id}']:
            await ctx.reply('Не лезь в игру богов, если сам не хочешь в нее играть!')
            return 0
        if len(persons['ruletka']) < 4:
            await ctx.send('Нужно как минимум 3 участника!')
        else:
            await ruletka_start(persons, ctx, self.bot, path)

    @commands.command(aliases=['kosti','roll'],description="Сыграть в кости с ботом. Можно сыграть на деньги\nНапример: /dice 10")
    @commands.guild_only()
    async def dice(self, ctx, total: typing.Optional[int] = 0):
        id = ctx.guild.id
        path = 'cogs/json_data/{}/users.json'.format(id)
        users = await open_json(path)
        if users[f'{ctx.author.id}']['cookies'] - total < 0:
            await ctx.reply('У тебя недостаточно фисташек!')
            return 0  
        bot1 = random.randint(1,6)
        bot2 = random.randint(1,6)
        user1 = random.randint(1,6)
        user2 = random.randint(1,6)
        await ctx.reply('У бота выпало {} и {}'.format(bot1,bot2))
        await asyncio.sleep(3)
        if user1 + user2 > bot1 + bot2:
            await ctx.reply('У тебя выпало {} и {}. Ты победил(а)!'.format(user1, user2))
            users[f'{ctx.author.id}']['cookies'] += total
        elif user1 + user2 == bot1 + bot2:
            await ctx.reply('У тебя выпало {} и {}. Ничья!'.format(user1, user2))
        else:
            await ctx.reply('У тебя выпало {} и {}. Ты проиграл(а)!'.format(user1, user2))
            users[f'{ctx.author.id}']['cookies'] -= total
            
        await save_data(users, 'cogs/json_data/{}/users.json'.format(id))

    #Gang style
    @commands.command(description="Ограбить любого участника на сервере.\nЗабирается от 0 до 20% включительно")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.guild_only()
    async def gang(self, ctx, member: discord.Member):
        guild_id = ctx.guild.id
        path = 'cogs/json_data/{}/users.json'.format(guild_id)
        user = member
        id = user.id
        users = await open_json(path)
        rand_percentage = random.randint(0,20)
        if member.bot:
            return 0
        if member == ctx.author:
            await ctx.reply('Ограбление века! Ты забрал все фисташки у самого себя!')
            return 0
        if rand_percentage == 0:
            await ctx.reply('Ты уже готовился ограбить {}, но тебя заметили. Хорошо, что ушел живым!'.format(member.mention))
        else:
            gang_amount = int(users[str(id)]['cookies']*(rand_percentage/100))
            users[str(id)]['cookies'] -= gang_amount
            users[f'{ctx.author.id}']['cookies'] += gang_amount
            await ctx.reply('Ты забрал кошель с деньгами у {}. Там было целых {} фисташек!'.format(member.mention, gang_amount))
            await save_data(users, path)

    @gang.error
    async def gang_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply('Тебе нужно отдохнуть после недавнего грабежа...')

    @commands.command(hidden=True, enabled=False)
    @commands.guild_only()
    async def bar(self, ctx, drink: typing.Optional[str] = 'Vodka', price: typing.Optional[int] = 10):
        message = f'Эй, бармен! {ctx.author.mention} просит оформить ему {drink} за {price}'
        guild_id = ctx.guild.id
        path = 'cogs/json_data/{}/bar.json'.format(guild_id)
        lots = await open_json(path)
        lots[f'{ctx.author.id}'] = {}
        lots[f'{ctx.author.id}']['drink'] = drink
        lots[f'{ctx.author.id}']['price'] = price      
        await ctx.reply(message)
        await save_data(lots, path)

    @commands.command(hidden=True, enabled=False)
    async def yes(self, ctx):
        if not ctx.author == self.barmen:
            return 0
        guild_id = ctx.guild.id
        path = 'cogs/json_data/{}/bar.json'.format(guild_id)
        lots = await open_json(path)
        print(random.choices(lots))
        drink = lots[f'{ctx.author.id}']['drink']
        price = lots[f'{ctx.author.id}']['price']
        await ctx.reply(f'Ты оформил {drink} за {price}')


    @commands.command(hidden=True)
    @commands.guild_only()
    async def set_barmen(self, ctx, member: discord.Member):
        self.barmen = member
        await ctx.reply(f'Поздравим {self.barmen.mention} с повышением до бармена!')

def setup(bot):
    bot.add_cog(GamesSystem(bot))