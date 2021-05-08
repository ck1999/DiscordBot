import discord, asyncio, typing, json, datetime
from discord.ext import commands

epoch = datetime.datetime.utcfromtimestamp(0)

async def open_json(name):
    with open(name, 'r') as f:
        return json.load(f)

async def save_data(array,name):
    with open(name, 'w') as f:
        json.dump(array, f)

async def add_experience(users, user, exp):
    time_diff = (datetime.datetime.utcnow() - epoch).total_seconds() - users[f'{user.id}']['xp_time']
    if time_diff >= 5:
        users[f'{user.id}']['experience'] += exp
        users[f'{user.id}']['xp_time'] = (datetime.datetime.utcnow() - epoch).total_seconds()

async def level_up(users, user, message):
        experience = users[f'{user.id}']['experience']
        lvl_start = users[f'{user.id}']['level']
        lvl_end = int(experience ** (1 / 4))
        if lvl_start < lvl_end:
            await message.channel.send(f'{user.mention} уже на {lvl_end} уровне!')
            users[f'{user.id}']['level'] = lvl_end
            users[f'{user.id}']['cookies'] += lvl_end*10

async def update_data(bank, users, user):
        if not f'{user.id}' in users:
            users[f'{user.id}'] = {}
            users[f'{user.id}']['experience'] = 0
            users[f'{user.id}']['level'] = 1
            users[f'{user.id}']['cookies'] = 100
            users[f'{user.id}']['xp_time'] = (datetime.datetime.utcnow() - epoch).total_seconds()
            users[f'{user.id}']['gang_time'] = 0
            bank[f'{user.id}'] = {}
            bank[f'{user.id}']['amount'] = 0

class RankSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
            
    @commands.Cog.listener()
    async def on_member_join(self, member):
        id = member.guild.id
        users = await open_json('cogs/json_data/{}/users.json'.format(id))
        bank = await open_json('cogs/json_data/{}/bank.json'.format(id))

        await update_data(bank, users, member)

        await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
        await save_data(bank, 'cogs/json_data/{}/bank.json'.format(id))

    @commands.Cog.listener()
    async def on_message(self, message):
        id = message.guild.id
        if message.author.bot == False:
            users = await open_json('cogs/json_data/{}/users.json'.format(id))
            bank = await open_json('cogs/json_data/{}/bank.json'.format(id))

            await update_data(bank, users, message.author)
            await add_experience(users, message.author, 5)
            await level_up(users, message.author, message)

            await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
            await save_data(bank, 'cogs/json_data/{}/bank.json'.format(id))

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        guild_id = ctx.guild.id
        if not member:
            id = ctx.message.author.id
            users = await open_json('cogs/json_data/{}/users.json'.format(guild_id))
            lvl = users[str(id)]['level']
            await ctx.send(f'У тебя уже {lvl} уровень!')
        else:
            id = member.id
            users = await open_json('cogs/json_data/{}/users.json'.format(guild_id))
            bank = await open_json('cogs/json_data/{}/bank.json'.format(guild_id))
            await update_data(bank, users, member)
            lvl = users[str(id)]['level']
            await ctx.send(f'У {member.mention} уже {lvl} уровень!')
            await save_data(users, 'cogs/json_data/{}/users.json'.format(guild_id))
            await save_data(bank, 'cogs/json_data/{}/bank.json'.format(guild_id))

def setup(bot):
    bot.add_cog(RankSystem(bot))