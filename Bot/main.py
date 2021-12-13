import os, discord
from discord.ext import commands, tasks
from utils.connector import SiteConnector
from utils.a_classes import AFor_Iter

from config import MAIN_TOKEN

class Meepy(commands.Bot):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(command_prefix=(self.get_prefix), *args, **kwargs)

        self.blacklist = set()
        self.add_check(self.check_user_blacklist)

    async def start(self, *args, **kwargs) -> None:

        self.connector = SiteConnector()
        await self.connector.setup()
        await bot.get_blacklisted()

        return await super().start(*args, **kwargs)

    async def close(self, reason: str = 'No reason') -> None:
        await self.connector.close_session(reason)
        return await super().close()

    async def get_blacklisted(self):
        data = await self.connector.get_data('blacklist')
        async for i in AFor_Iter(data):
            self.blacklist.add(i.get('user'))

    async def get_prefix(bot, message):
        try:
            data = await bot.connector.get_data(f'guilds/{message.guild.id}', True)
            prefix = data.get('prefix')
        except AttributeError:
            return '!'
        return prefix

    async def check_user_blacklist(self, ctx: commands.Context):
        if ctx.author.id in self.blacklist:
            raise commands.UserNotFound('Blacklisted')
        else:
            return True

intents = discord.Intents(guilds=True, messages=True, members=True, voice_states=True, bans=True)
bot = Meepy(intents=intents)

@bot.event
async def on_ready() -> None:
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'{filename[:-3]} loaded')
    bot.load_extension('jishaku')

bot.run(MAIN_TOKEN)