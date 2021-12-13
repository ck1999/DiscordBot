import asyncio
from random import choice, randint
from typing import Optional
from discord.ext import commands
from discord import Member
from config import COOLDOWN_CLASSIC, COOLDOWN_EXTRA

class GamesSystem(commands.Cog, name='Игры'):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        response = await self.bot.connector.get_data(f'guilds/{ctx.guild.id}', True)
        return response.get('setting_plugin_games')

    @commands.command(aliases=['kosti','roll'],description="Сыграть в кости с ботом. Можно сыграть на деньги\nНапример: /dice 10")
    @commands.cooldown(1, COOLDOWN_CLASSIC, commands.BucketType.user)
    @commands.guild_only()
    async def dice(self, ctx: commands.Context, amount: Optional[int] = 0):
        if amount < 0:
            return await ctx.reply('Прости, но мы не играем в долг...')
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{ctx.author.id}')
        __balance = response.get('balance') - amount
        if __balance < 0:
            return await ctx.reply('Кого ты пытаешься обмануть? Возвращайся с деньгами!')
        __bot_roll_1 = randint(1,6)
        __bot_roll_2 = randint(1,6)
        __user_roll_1 = randint(1,6)
        __user_roll_2 = randint(1,6)
        await ctx.reply(f'У бота выпало {__bot_roll_1} и {__bot_roll_2}')
        await asyncio.sleep(3)
        if __user_roll_1 + __user_roll_2 > __bot_roll_1 + __bot_roll_2:
            await ctx.reply(f'У тебя выпало {__user_roll_1} и {__user_roll_2}. Ты победил(а)!')
            if amount != 0:
                context = {
                    'balance': response.get('balance') + amount
                }
                await self.bot.connector.put_data(f'{ctx.guild.id}/{ctx.author.id}', data=context)
        elif __user_roll_1 + __user_roll_2 == __bot_roll_1 + __bot_roll_2:
            await ctx.reply(f'У тебя выпало {__user_roll_1} и {__user_roll_2}. Ничья!')
        else:
            if randint(1,100) == 69:
                await ctx.reply(f'У тебя выпало {__user_roll_1} и {__user_roll_2}, однако ты забрал деньги и убежал!')
                context = {
                    'balance': response.get('balance') + amount
                }
                await self.bot.connector.put_data(f'{ctx.guild.id}/{ctx.author.id}', data=context)
            else:
                await ctx.reply(f'У тебя выпало {__user_roll_1} и {__user_roll_2}. Ты проиграл(а)!')
                if amount != 0:
                    context = {
                        'balance': response.get('balance') - amount
                    }
                    await self.bot.connector.put_data(f'{ctx.guild.id}/{ctx.author.id}', data=context)

    @commands.command(description="Ограбить любого участника на сервере.\nЗабирается от 0 до 20% включительно")
    @commands.cooldown(1, COOLDOWN_EXTRA, commands.BucketType.member)
    @commands.guild_only()
    async def gang(self, ctx: commands.Context, member: Member = None):
        if member is None:
            return await ctx.reply('Ты так долго думал кого ограбить, что даже уснул...')
        if member.bot:
            return await ctx.reply('Ты попытался ограбить бога, но твое сознание помутнело и ты потерял сознание...')
        if member == ctx.author:
            return await ctx.reply('Ограбление века! Ты забрал все фисташки у самого себя!')
        __percentage = randint(0,20)
        if __percentage == 0:
            return await ctx.reply(f'Ты уже готовился ограбить {member.mention}, но тебя заметили. Хорошо, что ушел живым!')
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{member.id}')
        __amount = int(response.get('balance')*(__percentage/100))
        context = {
            'balance': response.get('balance') - __amount
        }
        await self.bot.connector.put_data(f'{ctx.guild.id}/{member.id}', data=context)
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{ctx.author.id}')
        context = {
            'balance': response.get('balance') + __amount
        }
        await self.bot.connector.put_data(f'{ctx.guild.id}/{ctx.author.id}', data=context)
        return await ctx.reply(f'Ты забрал кошель с деньгами у {member.mention}. Там было целых {__amount} фисташек!')

    @commands.command(aliases=['w'], description="Уйти работать на завод\nПример команды: !work")
    @commands.cooldown(1, COOLDOWN_EXTRA/2, commands.BucketType.member)
    @commands.guild_only()
    async def work(self, ctx: commands.Context):
        response = await self.bot.connector.get_data(f'{ctx.guild.id}/{ctx.author.id}')
        salary = randint(0,20)*response.get('level')
        if salary == 0:
            return await ctx.reply('Работадатель обманул тебя и не выплатил зарплату. Не переживай, все бывает!')
        context = {
            'balance': response.get('balance') + salary
        }
        await self.bot.connector.put_data(f'{ctx.guild.id}/{ctx.author.id}', data=context)
        await ctx.reply(f'Рабочий день окончен. Сегодня ты заработал(а) {salary}. Вполне неплохо!')
        
def setup(bot):
    bot.add_cog(GamesSystem(bot))