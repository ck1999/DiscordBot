import asyncio, requests
from random import choice, randint
from typing import Optional
from discord.ext import commands
from discord import ui, Member, ButtonStyle, Interaction
from .settings import settings

class RuletkaUI(ui.View):

    def __init__(self, summary: int):
        super().__init__()

        self.game = {}
        self.summary = summary

    async def create_game(self, id: int):
        if not self.game.get(id):
            self.game[id] = []

    @ui.button(label="Join", style=ButtonStyle.green)
    async def join(self, button: ui.Button, interaction: Interaction): 
        await self.create_game(interaction.guild.id)
        request = requests.get(settings.get('api')+f'{interaction.guild.id}/{interaction.user.id}')
        __balance = request.json().get('balance') - self.summary
        if __balance < 0:
            return await interaction.response.send_message('Кого ты пытаешься обмануть? Возвращайся с деньгами!', ephemeral=True)
        if interaction.user in self.game[interaction.guild.id]:
            return await interaction.response.send_message("Ты уже играешь! Жди начала игры!", ephemeral=True)
        self.game[interaction.guild.id].append(interaction.user)
        players_text = ''
        for i in self.game[interaction.guild.id]:
            players_text += f'{i.mention}\n'
        return await interaction.edit_original_message(content=f'**Игра находится в стадии разработки!**\n\n**ИГРОКИ:**\n{players_text}')

    @ui.button(label="Start", style=ButtonStyle.red)
    async def start(self, button: ui.Button, interaction: Interaction):
        await self.create_game(interaction.guild.id)
        length = len(self.game.get(interaction.guild.id))
        prize = self.summary * length
        if length < 2:
            return await interaction.response.send_message(f"Нужно как минимум 2 игрока!\nТекущее количество: {length}\nТекущий приз: {prize}", ephemeral=True)
        while len(self.game.get(interaction.guild.id)) > 1:
            user = choice(self.game[interaction.guild.id])
            request = requests.get(settings.get('api')+f'{interaction.guild.id}/{user.id}')
            context = {
                'balance': request.json().get('balance') - self.summary,
            }
            requests.put(settings.get('api')+f'{interaction.guild.id}/{user.id}', data=context)
            await interaction.response.send_message(f"Пуля летит прямо в {user.mention}")
            await asyncio.sleep(5)
        winner = self.game.get(interaction.guild.id)[0]
        request = requests.get(settings.get('api')+f'{interaction.guild.id}/{user.id}')
        context = {
            'balance': request.json().get('balance') + prize,
        }
        requests.put(settings.get('api')+f'{interaction.guild.id}/{winner.id}', data=context)
        await interaction.response.send_message(f"Всем спасибо за игру!\nВ живых остался только {winner.mention}\nОн забирает приз в размере: {prize}")
        return await interaction.delete_original_message()

    @ui.button(label="Leave", style=ButtonStyle.red)
    async def leave(self, button: ui.Button, interaction: Interaction):
        await self.create_game(interaction.guild.id)
        if not interaction.user in self.game[interaction.guild.id]:
            return await interaction.response.send_message("Ты еще не заходил в нашу прекрасную игру...", ephemeral=True)
        self.game[interaction.guild.id].remove(interaction.user)
        players_text = ''
        for i in self.game[interaction.guild.id]:
            players_text += f'{i.mention}\n'
        return await interaction.edit_original_message(content=f'**Игра находится в стадии разработки!**\n\n**ИГРОКИ:**\n{players_text}')

class GamesSystem(commands.Cog, name='Игры'):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['rr'],description="Проверяйте сами :)")
    @commands.cooldown(1, settings.get('cooldown_classic')*10, commands.BucketType.guild)
    @commands.guild_only()
    async def ruletka(self, ctx: commands.Context, summary: Optional[int] = 0):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_games'):
            return
        if summary is not None and summary < 0:
            return await ctx.reply(f'Может ты еще и антипули хочешь использовать? На {summary} он хочет играть...')
        return await ctx.reply('Ну, давайте попробуем собрать нужное количество!', view=RuletkaUI(summary=summary), delete_after=settings.get('cooldown_large')*10)

    @commands.command(aliases=['kosti','roll'],description="Сыграть в кости с ботом. Можно сыграть на деньги\nНапример: /dice 10")
    @commands.cooldown(1, settings.get('cooldown_classic'), commands.BucketType.user)
    @commands.guild_only()
    async def dice(self, ctx: commands.Context, amount: Optional[int] = 0):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_games'):
            return
        if amount < 0:
            return await ctx.reply('Прости, но мы не играем в долг...')
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}')
        __balance = request.json().get('balance') - amount
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
                    'balance': request.json().get('balance') + amount
                }
                requests.put(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}', data=context)
        elif __user_roll_1 + __user_roll_2 == __bot_roll_1 + __bot_roll_2:
            await ctx.reply(f'У тебя выпало {__user_roll_1} и {__user_roll_2}. Ничья!')
        else:
            if randint(1,100) == 69:
                await ctx.reply(f'У тебя выпало {__user_roll_1} и {__user_roll_2}, однако ты забрал деньги и убежал!')
                context = {
                    'balance': request.json().get('balance') + amount
                }
                requests.put(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}', data=context)
            else:
                await ctx.reply(f'У тебя выпало {__user_roll_1} и {__user_roll_2}. Ты проиграл(а)!')
                if amount != 0:
                    context = {
                        'balance': request.json().get('balance') - amount
                    }
                    requests.put(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}', data=context)

    @commands.command(description="Ограбить любого участника на сервере.\nЗабирается от 0 до 20% включительно")
    @commands.cooldown(1, settings.get('cooldown_day'), commands.BucketType.user)
    @commands.guild_only()
    async def gang(self, ctx: commands.Context, member: Member = None):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_games'):
            return
        if member is None:
            return await ctx.reply('Ты так долго думал кого ограбить, что даже уснул...')
        if member.bot:
            return await ctx.reply('Ты попытался ограбить бога, но твое сознание помутнело и ты потерял сознание...')
        if member == ctx.author:
            return await ctx.reply('Ограбление века! Ты забрал все фисташки у самого себя!')
        __percentage = randint(0,20)
        if __percentage == 0:
            return await ctx.reply(f'Ты уже готовился ограбить {member.mention}, но тебя заметили. Хорошо, что ушел живым!')
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{member.id}')
        __amount = int(request.json().get('balance')*(__percentage/100))
        context = {
            'balance': request.json().get('balance') - __amount
        }
        requests.put(settings.get('api')+f'{ctx.guild.id}/{member.id}', data=context)
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}')
        context = {
            'balance': request.json().get('balance') + __amount
        }
        requests.put(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}', data=context)
        return await ctx.reply(f'Ты забрал кошель с деньгами у {member.mention}. Там было целых {__amount} фисташек!')

    @gang.error
    async def gang_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.reply('Тебе нужно отдохнуть после недавнего грабежа...')

    @commands.command(aliases=['w'], description="Уйти работать на завод\nПример команды: !work")
    @commands.cooldown(1, settings.get('cooldown_day')/2, commands.BucketType.user)
    @commands.guild_only()
    async def work(self, ctx: commands.Context):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_games'):
            return
        request = requests.get(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}')
        salary = randint(0,20)*request.json().get('level')
        if salary == 0:
            return await ctx.reply('Работадатель обманул тебя и не выплатил зарплату. Не переживай, все бывает!')
        context = {
            'balance': request.json().get('balance') + salary
        }
        requests.put(settings.get('api')+f'{ctx.guild.id}/{ctx.author.id}', data=context)
        await ctx.reply(f'Рабочий день окончен. Сегодня ты заработал(а) {salary}. Вполне неплохо!')

    @work.error
    async def work_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.reply('У тебя болят все кости. Пожалуй, стоит немного отдохнуть...')

def setup(bot):
    bot.add_cog(GamesSystem(bot))