import discord, asyncio, typing, json, datetime, random
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

async def ruletka_start(rr, ctx, bot):
        await ctx.send('Да начнется игра!')
        rr.pop('ruletka')
        players = []

        users = await open_json('cogs/json_data/{}/users.json'.format(id))

        for k in rr:
            players.append(k)

        while len(players) > 1:
            await ctx.send('Я заряжаю патрон и...')
            member_id = random.choices(players)
            players.remove('{}'.format(member_id[0]))
            member = await bot.fetch_user('{}'.format(member_id[0]))
            users[f'{bot.user.id}'].pop('{}'.format(member_id[0]))
            await ctx.send('Убиваю {}!'.format(member.mention))
            await asyncio.sleep(5)


        member = await bot.fetch_user('{}'.format(players[0]))
        await ctx.send('Похоже, что остался только {}'.format(member.mention))
        await ctx.send('Поздравляю тебя с победой!')
        users[f'{member.id}']['cookies'] += rr['ruletka']['total']
        rr['ruletka']['total'] = 0
        rr['ruletka'].pop(f'{member.id}')

        await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
        await save_data(rr, 'cogs/json_data/{}/ruletka.json'.format(id))

class GamesSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ruletka(self, ctx, price: typing.Optional[int] = 0):
        
        id = ctx.guild.id
        users = await open_json('cogs/json_data/{}/users.json'.format(id))
        rr = await open_json('cogs/json_data/{}/ruletka.json'.format(id))

        if f'{ctx.author.id}' in rr['ruletka']:
            users[f'{ctx.author.id}']['cookies'] += rr['ruletka']['total']
            rr['ruletka']['total'] -= rr['ruletka'][f'{ctx.author.id}']
            rr['ruletka'].pop(f'{ctx.author.id}', None)
            await ctx.reply('Уже уходишь? Жаль...')
        else:
            if users[f'{ctx.author.id}']['cookies'] - price < 0:
                await ctx.reply('У тебя недостаточно фисташек!')
            else:
                rr['ruletka'][f'{ctx.author.id}'] = price
                users[f'{ctx.author.id}']['cookies'] -= price
                rr['ruletka']['total'] += price
                await ctx.reply('Теперь ты в игре, смертный!')
        
        await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
        await save_data(rr, 'cogs/json_data/{}/ruletka.json'.format(id))

    @commands.command()
    async def start(self, ctx):
        id = ctx.guild.id
        persons = await open_json('cogs/json_data/{}/ruletka.json'.format(id))

        if len(persons) < 4:
            await ctx.send('Нужно как минимум 3 участника!')
        else:
            await ruletka_start(persons, ctx, self.bot)

    @commands.command()
    async def dice(self, ctx, price: typing.Optional[int] = 0):
        id = ctx.guild.id
        users = await open_json('cogs/json_data/{}/users.json'.format(id))
        dice = await open_json('cogs/json_data/{}/dice.json'.format(id))
        if f'{ctx.author.id}' in dice:
            users[f'{ctx.author.id}']['cookies'] += dice[f'{ctx.author.id}']['amount']
            dice.pop(f'{ctx.author.id}', None)
            await ctx.reply('Боишься бросать кости? Без проблем, я тебя понимаю...')
        else:
            if users[f'{ctx.author.id}']['cookies'] - price < 0:
                    await ctx.reply('У тебя недостаточно фисташек!')
            else:
                dice[f'{ctx.author.id}'] = {}
                dice[f'{ctx.author.id}']['amount'] = price
                users[f'{ctx.author.id}']['cookies'] -= price
                await ctx.reply('Играем! Напиши /roll когда будешь готов')
            
        await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
        await save_data(dice, 'cogs/json_data/{}/dice.json'.format(id))

    @commands.command()
    async def roll(self, ctx):
        id = ctx.guild.id
        users = await open_json('cogs/json_data/{}/users.json'.format(id))
        dice = await open_json('cogs/json_data/{}/dice.json'.format(id))
        if f'{ctx.author.id}' in dice:
            bot1 = random.randint(1,6)
            bot2 = random.randint(1,6)
            user1 = random.randint(1,6)
            user2 = random.randint(1,6)
            await ctx.reply('У бота выпало {} и {}'.format(bot1,bot2))
            await asyncio.sleep(3)
            if user1 + user2 > bot1 + bot2:
                await ctx.reply('У тебя выпало {} и {}. Ты победил(а)!'.format(user1, user2))
                users[f'{ctx.author.id}']['cookies'] += dice[f'{ctx.author.id}']['amount']*2
            elif user1 + user2 == bot1 + bot2:
                await ctx.reply('У тебя выпало {} и {}. Ничья!'.format(user1, user2))
                users[f'{ctx.author.id}']['cookies'] += dice[f'{ctx.author.id}']['amount']
            else:
                await ctx.reply('У тебя выпало {} и {}. Ты проиграл(а)!'.format(user1, user2))
            dice.pop(f'{ctx.author.id}', None)
        else:
            await ctx.reply('Сначала сядь за стол и поздоровайся, а уже потом бросай кости!')

        await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
        await save_data(dice, 'cogs/json_data/{}/dice.json'.format(id))

    #Gang style
    @commands.command()
    async def gang(self, ctx, member: discord.Member = None):
        if not member or member.id == ctx.author.id:
            await ctx.send('И кого ты собрался грабить? Самого себя?')
        else:
            id = member.id
            guild_id = ctx.guild.id
            users = await open_json('cogs/json_data/{}/users.json'.format(guild_id))
            time_diff = (datetime.datetime.utcnow() - epoch).total_seconds() - users[f'{ctx.author.id}']['gang_time']
            if time_diff < 86400:
                await ctx.reply('{} пристально следит за своими вещами. Боюсь, что не выйдет...'.format(member.mention))
            else:
                await update_data(users, member, guild_id)
                users[f'{ctx.author.id}']['gang_time'] = (datetime.datetime.utcnow() - epoch).total_seconds()
                rand_percentage = random.randint(0,20)
                if rand_percentage == 0:
                    await ctx.reply('Ты уже готовился ограбить {}, но тебя заметили. Хорошо, что ушел живым!'.format(member.mention))
                else:
                    gang_amount = int(users[str(id)]['cookies']*(rand_percentage/100))
                    users[str(id)]['cookies'] -= gang_amount
                    users[f'{ctx.author.id}']['cookies'] += gang_amount
                    await ctx.reply('Ты забрал кошель с деньгами у {}. Там было целых {} фисташек!'.format(member.mention, gang_amount))
            await save_data(users, 'cogs/json_data/{}/users.json'.format(id))

def setup(bot):
    bot.add_cog(GamesSystem(bot))