import asyncio
from random import randint
from discord.ext import commands
from discord import Embed
from utils.a_classes import AFor
from utils.views import Race

class Casino(commands.Cog, name='Казино'):

    def __init__(self, bot) -> None:
        self.bot = bot

        self.emojis = {
            1: 911381805062565919,
            2: 911381805494575184,
            3: 911381805742030878,
            4: 911381805704290304,
            5: 911381805406494751,
            6: 911381805410680925,
            7: 911381805662363729,
            8: 911381805440061451,
            9: 911381805691732018
        }

    async def cog_check(self, ctx: commands.Context):
        response = await self.bot.connector.get_data(f'guilds/{ctx.guild.id}', True)
        return response.get('setting_plugin_games')

    @commands.command(name='race', description='Скачки', hidden=True)
    @commands.guild_only()
    async def make_race(self, ctx: commands.Context):
        view = Race(bid=15, started=False, timeout=60)
        bids = await ctx.reply('Ставки не будут приниматься через 60 секунд!', view=view)
        await view.wait()
        horse = await self.run_horses_run(bids)
        await view.game(horse, ctx)

    async def run_horses_run(self, message):
        horses = []
        async for i in AFor(1, 10, 1):
            horses.append(0)
        winner = 0
        embed = Embed(color=0x2F3136)
        for i in range(9):
                before = horses[i]*'⬛'
                after = (19-horses[i])*'⬛'+'🏁'
                emoji = self.bot.get_emoji(self.emojis.get(i+1))
                embed.add_field(name='\u200B', value=f'{before}{emoji}{after}', inline=False)
        await message.edit(content='', embed=embed, view=None)
        while winner == 0:
            await asyncio.sleep(1)
            for i in range(len(horses)):
                horses[i] += randint(1,3)   
                if horses[i] >= 19:
                    if winner == 0:
                        horses[i] = 19
                        winner = i+1
                    else:
                        horses[i] = 18 #Add horses to winner list.
            embed = Embed(color=0x2F3136)
            for i in range(9):
                before = horses[i]*'⬛'
                after = (19-horses[i])*'⬛'+'🏁'
                emoji = self.bot.get_emoji(self.emojis.get(i+1))
                embed.add_field(name='\u200B', value=f'{before}{emoji}{after}', inline=False)
            await message.edit(embed=embed, view=None)
        await message.delete(delay=120)
        return winner

def setup(bot):
    bot.add_cog(Casino(bot))