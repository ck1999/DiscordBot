import typing, datetime
from discord.ext import commands
from discord import Embed, Member, Role
from utils.views import CRV, CustomRolesButton

from config import COOLDOWN_LARGE

class AdminCommands(commands.Cog, name='Модераторство'):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx: commands.Context):
        response = await self.bot.connector.get_data(f'guilds/{ctx.guild.id}', True)
        return response.get('setting_plugin_admin')

    @commands.command(description="Бан пользователя. Можно вводить несколько пользователей.\nЕсли нужно, то можно указать кол-во дней, за которые нужно удалить все сообщения и причину")
    @commands.has_permissions(ban_members=True, administrator=True)
    async def ban(self, ctx, members: commands.Greedy[Member], delete_days: typing.Optional[int] = 0, *, reason: typing.Optional[str] = "Без причины"):
        if ctx.guild.system_channel is not None:
            log = ctx.guild.system_channel

        for member in members:
            await member.ban(delete_message_days=delete_days, reason=reason)
            embed = Embed(title="Участника забанили", timestamp=datetime.datetime.utcnow())
            embed.add_field(name=f'Участник:', value=f'{member.mention}', inline=True)
            embed.add_field(name=f'Модератор:', value=f'{ctx.author.mention}', inline=True)
            embed.add_field(name=f'Причина:', value=f'{reason}', inline=True)
            embed.set_footer(text=f'ID: {member.id}')
            await log.send(embed=embed)

    @commands.command(description="Кик пользователя. Можно вводить несколько пользователей.\nЕсли нужно, то можно указать причину")
    @commands.has_permissions(kick_members=True, administrator=True)
    @commands.guild_only()
    async def kick(self, ctx, members: commands.Greedy[Member], *, reason: typing.Optional[str] = "Без причины"):
        if ctx.guild.system_channel is not None:
            log = ctx.guild.system_channel

        for member in members:
            await member.kick(reason=reason)
            embed = Embed(title="Участника кикнули", timestamp=datetime.datetime.utcnow())
            embed.add_field(name=f'Участник:', value=f'{member.mention}', inline=True)
            embed.add_field(name=f'Модератор:', value=f'{ctx.author.mention}', inline=True)
            embed.add_field(name=f'Причина:', value=f'{reason}', inline=True)
            embed.set_footer(text=f'ID: {member.id}')
            await log.send(embed=embed)

    @commands.command(description="Дата, когда пользователь зашел на сервер")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def joined(self, ctx, *, member: Member):
        await ctx.send(f'{member} зашел на сервер {member.joined_at}')

    @commands.command(hidden=True,description="Инфа об юзере + гильде")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def info(self, ctx: commands.Context, member: Member):
        await ctx.send(f'**Юзер найден: **\n**ID:** {member.id}\n**Никнейм:** {member.mention}')
        await ctx.send(f'**Сервер найден: **\n**ID** {ctx.guild.id}')

    @commands.command(hidden=True, aliases=['set', 'log'],description="Сделать канал хранилищем логов *")
    # @commands.cooldown(5, 600, commands.BucketType.guild)
    @commands.guild_only()
    async def set_log(self, ctx: commands.Context, role: Role):
        roles = [
            (839480527718711376, None),
            (914878242350051348, None)
        ]
        ind = roles.index((role.id,))
        print(ind)
        # obj = (role.id,)
        # self.roles.remove()

    @commands.command(description="Очистка чата. AXTUNG! Работает оооочень медленно, зато с плюшками!")
    @commands.cooldown(5, COOLDOWN_LARGE, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def clear(self, ctx, number: int, user: Member = None):
        msg = await ctx.channel.history(limit=number).flatten()
        count = 0
        if user is not None:
            for i in msg:
                if i.author == user:
                    await i.delete()
                    count += 1
        else:
            for i in msg:
                await i.delete()
                count += 1
        await ctx.reply(f'Завершено. Удалено {count} сообщений!')

    @commands.group(name='cr', invoke_without_command=True)
    @commands.guild_only()
    async def custom_role_group(self, ctx: commands.Context):
        embed = Embed(color=0x2F3136, title='CR',description='')
        for command in self.custom_role_group.walk_commands():
            embed.description += f'{command.name} - {command.description}\n'
        return await ctx.reply(embed=embed)

    @custom_role_group.command(name='create', description='Создает меню для выдачи ролей')
    @commands.guild_only()
    async def custom_view_create(self, ctx: commands.Context):
        return await ctx.send('Меню успешно создано! Осталось лишь его настроить...')

    @custom_role_group.command(name='add', description='Добавляет кнопку с получением роли. Нужно ответить на сообщение с меню, где это все будет!')
    @commands.guild_only()
    async def custom_view_add(self, ctx: commands.Context, role: Role, *, text: str):
        message = await ctx.fetch_message(ctx.message.reference.message_id)
        view = CRV()
        for row in message.components:
            for component in row.children:
                data = component.custom_id.split('|')
                __role = ctx.guild.get_role(int(data[0]))
                await view.crv_add(__role, data[1], component.custom_id)
        await view.crv_add(role, text, custom_id=f'{role.id}|{text}')
        await message.edit('Menu', view=view)

def setup(bot):
    bot.add_cog(AdminCommands(bot))