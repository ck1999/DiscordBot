import discord, time
from discord.ext import commands
from config import COOLDOWN_LARGE

class Birthday(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
    
    # @commands.command()
    # async def set_birthday(self, ctx, date, member: discord.Member = None):
    #     id = ctx.guild.id
        
    #     date = date.split('-')
    #     for i in range(len(date)):
    #         date[i] = int(date[i])

    #     if member == None:
    #         if len(date) == 2:
    #             birthday_date[f'{ctx.author.id}']['birthday_month'] = date[0]
    #             birthday_date[f'{ctx.author.id}']['birthday_day'] = date[1]
    #         elif len(date) == 3:
    #             birthday_date[f'{ctx.author.id}']['birthday_year'] = date[0]
    #             birthday_date[f'{ctx.author.id}']['birthday_month'] = date[1]
    #             birthday_date[f'{ctx.author.id}']['birthday_day'] = date[2]
    #     else:
    #         if len(date) == 2:
    #             birthday_date[f'{member.id}']['birthday_month'] = date[0]
    #             birthday_date[f'{member.id}']['birthday_day'] = date[1]
    #         elif len(date) == 3:
    #             birthday_date[f'{member.id}']['birthday_year'] = date[0]
    #             birthday_date[f'{member.id}']['birthday_month'] = date[1]
    #             birthday_date[f'{member.id}']['birthday_day'] = date[2]
    #     await save_data(birthday_date, 'cogs/json_data/{}/birthday.json'.format(id))
            
    # @commands.command()
    # async def birthday(self, ctx, member: discord.Member = None):
    #     id = ctx.guild.id
    #     users = await open_json('cogs/json_data/{}/users.json'.format(id))
    #     bank = await open_json('cogs/json_data/{}/bank.json'.format(id))

    #     await update_data(bank, users, ctx.author)

    #     if member == None:
    #         if users[f'{ctx.author.id}']['birthday_day'] == 0:
    #             await ctx.reply('Я не знаю когда был рожден такой цветок жизни!')
    #         elif users[f'{ctx.author.id}']['birthday_year'] == 1:
    #             await ctx.reply('Хм. Ты был рожден {}.{}'.format(users[f'{ctx.author.id}']['birthday_day'],users[f'{ctx.author.id}']['birthday_month']))
    #         else:
    #             await ctx.reply('Ты был рожден {}.{}.{}'.format(users[f'{ctx.author.id}']['birthday_day'],users[f'{ctx.author.id}']['birthday_month'], users[f'{ctx.author.id}']['birthday_year']))
    #     else:
    #         await update_data(bank, users, member)
    #         if users[f'{member.id}']['birthday_day'] == 0:
    #             await ctx.reply('Я не знаю когда был рожден такой цветок жизни!')
    #         elif users[f'{member.id}']['birthday_year'] == 1:
    #             await ctx.reply('Хм. Он был рожден в {}.{}'.format(users[f'{member.id}']['birthday_day'],users[f'{member.id}']['birthday_month']))
    #         else:
    #             await ctx.reply('Он был рожден {}.{}.{}'.format(users[f'{member.id}']['birthday_day'],users[f'{member.id}']['birthday_month'],users[f'{member.id}']['birthday_year']))
    #     await save_data(users, 'cogs/json_data/{}/users.json'.format(id))
    #     await save_data(bank, 'cogs/json_data/{}/bank.json'.format(id))

class RankSystem(commands.Cog, name='Уровни'):

    def __init__(self, bot):
        self.bot = bot
            
    @commands.Cog.listener()
    async def on_member_join(self, member):
        context = {
            'guild': member.guild.id,
            'user': member.id,
            'balance': 100,
            'exp': 0,
            'level': 1,
            'xp_time_lock': time.time()
        }
        await self.bot.connector.post_data(f'{member.guild.id}', data=context)
        
    async def cog_check(self, ctx: commands.Context):
        response = await self.bot.connector.get_data(f'guilds/{ctx.guild.id}', True)
        return response.get('setting_plugin_rank')

    @commands.Cog.listener()
    async def on_message(self, message: str):
        if not message.guild:
            return
        response = await self.bot.connector.get_data(f'guilds/{message.guild.id}', True)
        try:
            if message.author.bot or not response.get('setting_plugin_rank') or message.content.startswith(response.get('prefix')):
                return
        except:
            return
        response = await self.bot.connector.get_data(f'{message.guild.id}/{message.author.id}')
        time_diff = time.time() - response.get('xp_time_lock')
        if time_diff >= 5:
            __exp = response.get('exp') + 5
            __level = response.get('level')
            __cookies = response.get('balance')
            if __exp**(1/4) > __level:
                __level += 1
                __cookies += __level*10
                await message.reply(f'{message.author.mention} достиг {__level} уровня!')
            context = {
                'level': __level,
                'exp': __exp,
                'balance': __cookies,
                'xp_time_lock': time.time()
            }
            await self.bot.connector.put_data(f'{message.guild.id}/{message.author.id}', data=context)

    @commands.command(description="Информация об уровне\nПримеры команд:\n!level\n!level @ck1999")
    @commands.cooldown(1, COOLDOWN_LARGE, commands.BucketType.user)
    @commands.guild_only()
    async def level(self, ctx, member: discord.Member = None):
        user = member or ctx.message.author
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{user.id}')
        await ctx.send(f"У {user.mention} уже {response.get('level')} уровень!")

def setup(bot):
    bot.add_cog(RankSystem(bot))
    #bot.add_cog(Birthday(bot))