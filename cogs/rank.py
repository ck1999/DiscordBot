import discord, time, requests
from discord.ext import commands
from .settings import settings

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
        request = requests.post(settings.get('api')+f'{member.guild.id}', data=context)
        

    @commands.Cog.listener()
    async def on_message(self, message: str):
        if message.guild is None or message.content.startswith('!') or message.author.bot:
            return
        request = requests.get(settings.get('api')+f'guilds/{message.guild.id}')
        if not request.json().get('setting_plugin_rank'):
            return
        request = requests.get(settings.get('api')+f'{message.guild.id}/{message.author.id}')
        time_diff = time.time() - request.json().get('xp_time_lock')
        if time_diff >= 5:
            __exp = request.json().get('exp') + 5
            __level = request.json().get('level')
            __cookies = request.json().get('balance')
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
            request = requests.put(settings.get('api')+f'{message.guild.id}/{message.author.id}', data=context)

    @commands.command(description="Информация об уровне\nПримеры команд:\n!level\n!level @ck1999")
    @commands.cooldown(1, settings.get('cooldown_large'), commands.BucketType.user)
    @commands.guild_only()
    async def level(self, ctx, member: discord.Member = None):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_rank'):
            return 0
        user = member or ctx.message.author
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{user.id}')
        await ctx.send('У {} уже {} уровень!'.format(user.mention, request.json().get('level')))

def setup(bot):
    bot.add_cog(RankSystem(bot))
    #bot.add_cog(Birthday(bot))