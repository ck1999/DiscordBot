from discord.ext import commands
from datetime import date, datetime
import pandas as pd
from functools import partial
from asyncio import BaseEventLoop

class Analyze(commands.Cog):

    def __init__(self, bot, loop: BaseEventLoop) -> None:
        self.bot = bot
        self.loop = loop

    @commands.Cog.listener()
    async def on_message(self, message: str):
        if not message.guild:
            return
        response = await self.bot.connector.get_data(f'guilds/{message.guild.id}', True)
        if not message.content.startswith(response.get('prefix')) or len(message.content) < 3:
            return
        content = message.content.split()
        user = f'{message.author.name}#{message.author.discriminator}'
        await self.loop.run_in_executor(None, partial(self.write_csv, message.guild.id, user, content[0]))

    def read_csv_data(self):
        name = 'other/data/' + date.today().strftime('%Y-%m-%d') + '.csv'
        header = ['Guild', 'User', 'CMD', 'Time']
        df = pd.read_csv(name, names=header)
        return df

    def write_csv(self, guild_id: int, user: str, command: str) -> None:
        df = pd.DataFrame({
            'guild': [guild_id],
            'user': [user],
            'command': [command],
            'time': [datetime.now().strftime('%H:%M:%S')]
        })
        name = 'other/data/' + date.today().strftime('%Y-%m-%d') + '.csv'
        df.to_csv(name, mode='a', index=False, header=None)

    @commands.command(name='df', hidden=True)
    @commands.is_owner()
    async def return_df(self, ctx: commands.Context):
        df = await self.loop.run_in_executor(None, self.read_csv_data)
        return await ctx.reply(df)

def setup(bot):
    bot.add_cog(Analyze(bot, bot.loop))