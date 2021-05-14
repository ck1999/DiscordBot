from discord.ext import commands
import discord, asyncio, time, json, os, datetime

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
        if filename == 'users':
            array = await create_user(array,user)
    await save_data(array, path)

async def create_user(array, user):
    array[f'{user.id}'] = {}
    array[f'{user.id}']['experience'] = 0
    array[f'{user.id}']['level'] = 1
    array[f'{user.id}']['cookies'] = 100
    array[f'{user.id}']['XP_TIME_LOCK'] = time.time()
    return array

class Basic(commands.Cog, name='Basic'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load_coag(self, ctx, name):
        self.bot.load_extension(f'cogs.{name}')
        time = datetime.datetime.now().strftime('%H:%M:%S')
        print(f'{name} loaded. Time: {time}')
        await asyncio.sleep(3)
        await ctx.message.delete()

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload_coag(self, ctx, name):
        self.bot.unload_extension(f'cogs.{name}')
        time = datetime.datetime.now().strftime('%H:%M:%S')
        print(f'{name} unloaded. Time: {time}')
        await asyncio.sleep(3)
        await ctx.message.delete()

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload_coag(self, ctx, name):
        self.bot.unload_extension(f'cogs.{name}')
        self.bot.load_extension(f'cogs.{name}')
        time = datetime.datetime.now().strftime('%H:%M:%S')
        print(f'{name} reloaded. Time: {time}')
        await asyncio.sleep(3)
        await ctx.message.delete()

    @commands.command(name='change', hidden=True)
    @commands.is_owner()
    async def change(self, ctx, game):
        await self.bot.change_presence(activity=discord.Game(game))
        await ctx.reply(f'Discord.game was changed to {game}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        os.chdir('cogs/json_data/')
        os.mkdir('{}'.format(guild.id))
        os.chdir('{}'.format(guild.id))
        with open('users.json', mode='w') as f:
            json.dump({}, f)
        with open('bank.json', mode='w') as f:
            json.dump({}, f)
        with open('bar.json', mode='w') as f:
            json.dump({}, f)
        with open('guild.json', mode='w') as f:
            json.dump({"main": {}}, f)
        with open('ruletka.json', mode='w') as f:
            json.dump({"ruletka": {"total": 0}}, f)
        with open('birthday.json', mode='w') as f:
            json.dump({}, f)
        
        os.chdir('../../..')

        async for user in guild.fetch_members(limit=None):
            if not user.bot:
                await update_data('users', user, guild.id)

        await guild.owner.send('Oops. Sorry for spam! I will be add something here later! Chao!\n(C) ck1999')
        
    @commands.Cog.listener()
    async def on_command_error(self, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        if isinstance(error, TypeError):
            raise error

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game('!help'))

def setup(bot):
    bot.add_cog(Basic(bot))