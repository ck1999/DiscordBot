from discord.ext import commands
from discord import Embed, Game, Permissions
import asyncio
from time import time
from discord.utils import oauth_url
from psutil import Process, virtual_memory
from platform import python_version
from datetime import timedelta
from discord import __version__ as dpy__version

class Basic(commands.Cog, name='Настройки'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', hidden=True)
    @commands.is_owner()
    async def pong(self, ctx: commands.Context):
        return await ctx.send(f"Pong! {self.bot.latency*1000:,.0f} мс")

    @commands.command(name='perms', hidden=True)
    @commands.is_owner()
    async def check_perms(self, ctx: commands.Context):
        perms = ctx.guild.me.guild_permissions
        embed = Embed(title="Permissions", description="", colour=0x2F3136)
        embed.add_field(name='Main', value=f'Read MSG: `{perms.read_messages}`\nSend MSG: `{perms.send_messages}`\nReactions: `{perms.add_reactions}`')
        embed.add_field(name='Voice', value=f'Connect: `{perms.connect}`\nSpeak: `{perms.speak}`')
        embed.add_field(name='Admin', value=f'Admin: `{perms.administrator}`\nKick: `{perms.kick_members}`\nBan: `{perms.ban_members}`\nMute: `{perms.mute_members}`')
        embed.add_field(name='Info', value=f':shield: Guild: `{ctx.guild.name}`\n:id: ID: `{ctx.guild.id}`\n')
        await ctx.author.send(embed=embed)

    @commands.command(name='block', hidden=True)
    @commands.is_owner()
    async def add_user_to_blacklist(self, ctx: commands.Context, id: int):
        self.bot.blacklist.add(id)
        print(self.bot.blacklist)
        return await ctx.reply('Added!', delete_after=300)

    @commands.command(name='stats', hidden=True)
    @commands.is_owner()
    async def get_stats(self, ctx: commands.Context):
        embed = Embed(title=":bar_chart: Statistic", description="", colour=0x2F3136)
        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time()-proc.create_time())
            # cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
            # mem_total = virtual_memory().total / (1024**2)
            # mem_of_total = proc.memory_percent()
            # mem_usage = mem_total * (mem_of_total / 100)
        fields = [
            (":shield: Guilds", f'`{len(self.bot.guilds)}`'),
            (":speech_balloon: Users", f'`{len(self.bot.users)}`'),
            (":sound: Voices", f'`{len(self.bot.voice_clients)}`'),
            (":wrench: Python", f'`{python_version()}`'),
            (":hammer: DPY", f'`{dpy__version}`'),
            (":clock1: Uptime", f'`{uptime}`')
        ]
        embed.set_footer(text='ck1999#9507 | https://discord.gg/yCaMMg9XmD')
        for name, value in fields:
            embed.description += f'**{name}:**     {value}\n'
        return await ctx.reply(embed=embed, delete_after=300)

    @commands.command(name='invites', hidden=True)
    @commands.is_owner()
    async def get_invites(self, ctx: commands.Context):
        embed = Embed(title=":incoming_envelope: Invites", description="", colour=0x2F3136)
        async for guild in self.bot.fetch_guilds(limit=30):
            guild = await self.bot.fetch_guild(guild.id)
            try:
                invites = await guild.invites()
                embed.description += f'[{guild.name}]({invites[0].url})\n'
            except IndexError:
                embed.description += f'{guild.name} - NO INVITES\n'
            except:
                embed.description += f'{guild.name} - NO PERMS\n'
        return await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        context = {
            'guild_id': guild.id,
            'name': guild.name,
            'setting_plugin_music': False,
            'setting_plugin_games': False,
            'setting_plugin_admin': False,
            'setting_plugin_birthday': False,
            'setting_plugin_economy': False,
            'setting_plugin_rank': False,
            'prefix': '!'
        }
        await self.bot.connector.post_data('guilds', data=context)
        async for user in guild.fetch_members(limit=None):
            if not user.bot:
                context = {
                    'guild': guild.id,
                    'user': user.id,
                    'balance': 100,
                    'exp': 0,
                    'level': 1,
                    'xp_time_lock': time()
                }
                await self.bot.connector.post_data(f'{guild.id}', data=context)

    @commands.command(name='ticket')
    async def send_ticket_to_me(self, ctx: commands.Context):
        await ctx.reply('Пожалуйста, отправьте следующим сообщением полное описание проблемы.\n**Если проблема критическая, то просьба написать это в сервер поддержки!**', delete_after=300)

        def checking_message(message):
            return message.author == ctx.author

        try:
            message = await self.bot.wait_for('message', check=checking_message, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.reply('Ладно, забыли это дело. Если решишься все-таки что-то сказать, то обязательно дай знать!', delete_after=300)
        await message.reply('Успешно отправлено!')
        tickets_channel = await self.bot.fetch_channel(908600066141466624)
        if ctx.guild:
            return await tickets_channel.send(f'```{message}```\n\n**User:** `{message.author.id}`\n**Guild:** `{ctx.guild.id}`\n**CTX:** `{ctx.channel.id}`\n**Message:** `{ctx.message.id}`')
        else:
            return await tickets_channel.send(f'```{message}```\n\n**User:** `{message.author}`\n**Message:** `{ctx.message.id}`')

    @commands.command(name='answer', hidden=True)
    @commands.is_owner()
    async def answer_to_ticket(self, ctx: commands.Context, message_id: str, channel_id: str = None):
        channel = await self.bot.fetch_channel(channel_id)
        if not channel:
            return await ctx.reply('Такого канала больше нет', delete_after=300)
        message = await channel.fetch_message(message_id)
        if not message:
            return await ctx.reply('Такого сообщения больше нет', delete_after=300)
        await ctx.reply('Введите ответное сообщение!', delete_after=300)
        try:
            answer = await self.bot.wait_for('message', timeout=300)
        except asyncio.TimeoutError:
            return await ctx.reply('Вы забыли ввести ответное сообщение!', delete_after=300)

        return await message.reply(answer)

    @commands.command(name='invite')
    async def invite_bot(self, ctx: commands.Context):
        url = oauth_url(704454450386829543, permissions=Permissions(8))
        embed = Embed(title=":love_letter:   Заказное письмо", description="Здесь ты можешь найти мой адрес, дабы пригласить меня в свой замок!", colour=0x2F3136)
        embed.add_field(name=':link: Рекомендуемая ссылка:', value=f'[Клик-Клак]({url})')
        embed.add_field(name=':pushpin: Минимум прав:', value=f'В разработке', inline=False)
        embed.add_field(name=':pushpin: Только для музыки:', value=f'В разработке')
        return await ctx.reply(embed=embed)

    @commands.command(name='prefix', description='Поменять префикс для сервера')
    @commands.cooldown(5, 86400, commands.BucketType.guild)
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def change_prefix(self, ctx: commands.Context, prefix: str = '!'):
        if len(prefix) > 2:
            return await ctx.reply('Префикс не может быть больше 2 символов!', delete_after=300)
        data = {
            'prefix': prefix
        }
        await self.bot.connector.put_data(f'guilds/{ctx.guild.id}', data=data)
        return await ctx.reply('Команда выполнена успешно!', delete_after=300)

def setup(bot):
    bot.add_cog(Basic(bot))