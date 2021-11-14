from discord.ext import commands
from discord import Embed, Game, Forbidden
import asyncio, requests
from .settings import settings
import time

class Basic(commands.Cog, name='Basic'):
    def __init__(self, bot):
        self.bot = bot
        self.y = '\<y:907808729028780062>'
        self.x = '\<x:907808728898756608>'
        self.n = '\<no:907985288633139210>'

    @commands.group(name='settings', invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def settings(self, ctx: commands.Context):
        embed = Embed(title="Settings", description="", colour=0x2F3136)
        embed.add_field(name = ":control_knobs: **Cogs**", value= "`Reload`\n`Load`\n`Unload`", inline=False)
        embed.add_field(name = ":shield: **Guilds**", value= "`Invite`\n`Perms`\n`Fix`", inline=False)
        embed.add_field(name = ":hammer_pick: **Bot**", value="`Reset`\n`Game`", inline=False)
        embed.add_field(name = ":game_die: **Another**", value="`Print`\n`Check`\n`Stats`", inline=False)
        return await ctx.reply(embed=embed, delete_after=300)

    @settings.command(name='print', hidden=True)
    @commands.is_owner()
    async def print_line_in_console(self, ctx: commands.Context):
        print('----------------------------------------------------------------')
        return await ctx.message.add_reaction(self.y)

    @settings.command(name='invite', hidden=True)
    @commands.is_owner()
    async def create_invite_in_guild(self, ctx: commands.Context):
        embed = Embed(title="Settings", description="", colour=0x2F3136)
        embed.description += "`CURRENTLY NOT WORKING`"
        await ctx.reply(embed=embed, delete_after=300)

    @settings.command(name='perms', hidden=True)
    @commands.is_owner()
    async def check_perms(self, ctx: commands.Context):
        perms = ctx.guild.me.guild_permissions
        embed = Embed(title="Permissions", description="", colour=0x2F3136)
        embed.add_field(name='Main', value=f'Read MSG: `{perms.read_messages}`\nSend MSG: `{perms.send_messages}`\nReactions: `{perms.add_reactions}`')
        embed.add_field(name='Voice', value=f'Connect: `{perms.connect}`\nSpeak: `{perms.speak}`')
        embed.add_field(name='Admin', value=f'Admin: `{perms.administrator}`\nKick: `{perms.kick_members}`\nBan: `{perms.ban_members}`\nMute: `{perms.mute_members}`')
        embed.add_field(name='Info', value=f':shield: Guild: `{ctx.guild.name}`\n:id: ID: `{ctx.guild.id}`\n:clipboard: Role number: `{ctx.guild.self_role.position}`')
        await ctx.author.send(embed=embed)

    @settings.command(name='load', hidden=True)
    @commands.is_owner()
    async def load_coag(self, ctx: commands.Context, name: str):
        self.bot.load_extension(f'cogs.{name}')
        return await ctx.message.add_reaction(self.y)

    @settings.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload_coag(self, ctx: commands.Context, name: str):
        self.bot.load_extension(f'cogs.{name}')
        return await ctx.message.add_reaction(self.y)

    @settings.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload_coag(self, ctx: commands.Context, name: str):
        self.bot.unload_extension(f'cogs.{name}')
        self.bot.load_extension(f'cogs.{name}')
        return await ctx.message.add_reaction(self.y)

    @settings.command(name='reset', hidden=True)
    @commands.is_owner()
    async def reload_settings(self, ctx: commands.Context):
        self.bot.unload_extension('cogs.settings')  
        self.bot.load_extension('cogs.settings')
        return await ctx.message.add_reaction(self.y)

    @settings.command(name='game', hidden=True)
    @commands.is_owner()
    async def change(self, ctx: commands.Context, *, game: str):
        await self.bot.change_presence(activity=Game(game))
        return await ctx.message.add_reaction(self.y)

    @settings.command(name='check', hidden=True)
    @commands.is_owner()
    async def site_state_check(self, ctx: commands.Context):
        try:
            requests.get(settings.get('api')+f'settings/1')
            return await ctx.message.add_reaction(self.y)
        except:
            return await ctx.message.add_reaction(self.x)

    @settings.command(name='stats', hidden=True)
    @commands.is_owner()
    async def get_stats(self, ctx: commands.Context):
        embed = Embed(title=":bar_chart: Statistic", description="", colour=0x2F3136)
        embed.description += f":shield: I'm in: {len(self.bot.guilds)} guilds\n"
        embed.description += f":speech_balloon: Total users: {len(self.bot.users)}\n"
        embed.description += f":reminder_ribbon: Connected to: {len(self.bot.voice_clients)} voices\n"
        return await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        context = {
            'guild_id': guild.id,
            'name': guild.name
        }
        requests.post(settings.get('api')+'guilds', data=context)
        async for user in guild.fetch_members(limit=None):
            if not user.bot:
                context = {
                    'guild': guild.id,
                    'user': user.id,
                    'balance': 100,
                    'exp': 0,
                    'level': 1,
                    'xp_time_lock': time.time()
                }
                requests.post(settings.get('api')+f'{guild.id}', data=context)
        
        log = await self.bot.fetch_channel(settings['log'])
        return await log.send(f'**NEW GUILD:** {guild.id}\n**USERS:** {guild.humans}')

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
        await message.add_reaction(self.y)
        tickets_channel = await self.bot.fetch_channel(settings['ticket'])
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

        await ctx.channel.delete(delay=300)
        return await message.reply(answer)

    @commands.Cog.listener()
    async def on_command_error(self, object, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await object.reply(f'Не торопись, ковбой! Подожди еще {error.retry_after:.1f} секунд(ы).')
        if isinstance(error, commands.CommandNotFound):
            return await object.reply('Ты перепутал бота, дружок!')
        if isinstance(error, commands.DisabledCommand):
            return await object.reply('Пока что команда выключена. Мы ее обязательно вернем!')
        if isinstance(error, commands.MessageNotFound):
            return
        if isinstance(error, commands.NotOwner):
            return await object.message.add_reaction(self.n)
        print('----------------------------------------------------------------')
        try:
            await object.message.add_reaction(self.x)
            await object.reply('Произошло недоразумение. Сделайте тикет в тех. поддержку, если такое повторяется постоянно\nТикет можно отправить в личные сообщения боту\nОтправить тикет: !ticket')
        except Forbidden:
            pass
        log = await self.bot.fetch_channel(settings['log'])
        await log.send(f'**ERROR WITH CMD:** `{object.message.content}`')
        raise error

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=Game('!help'))

def setup(bot):
    bot.add_cog(Basic(bot))