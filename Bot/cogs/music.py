import lavalink
from discord.ext import commands
from discord import abc, VoiceClient, Client, Embed
from utils.views import PlayView
from utils.a_classes import AFor_Iter
from functools import partial
from other.spotify import get_tracks
from config import RURL, SPOTIFY_RURL

class LavalinkVoiceClient(VoiceClient):

    def __init__(self, client: Client, channel: abc.Connectable):
        self.client = client
        self.channel = channel
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                    'localhost',
                    2333,
                    'youshallnotpass',
                    'us',
                    'default-node')
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        lavalink_data = {
                't': 'VOICE_SERVER_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        lavalink_data = {
                't': 'VOICE_STATE_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: bool = False) -> None:

        player = self.lavalink.player_manager.get(self.channel.guild.id)

        if not player.is_connected and not force:
            return

        await self.channel.guild.change_voice_state(channel=None)

        player.channel_id = None
        self.cleanup()

    async def fix_voice_state(self):
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        await self.channel.guild.change_voice_state(channel=None)

        player.channel_id = None
        self.cleanup()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(704454450386829543)
            bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'eu', 'default-node')

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_check(self, ctx: commands.Context):
        response = await self.bot.connector.get_data(f'guilds/{ctx.guild.id}', True)
        
        if response.get('setting_plugin_music'):
            if not ctx.message.content[1:].startswith('help'):
                return await self.ensure_voice(ctx)
            else:
                return True
        return False

    async def ensure_voice(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply('Сначала зайди в любой голосовой канал!', delete_after=60)
            return False

        if not player.is_connected:

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect:
                await ctx.reply('Извини, но я не вижу куда заходить. Может дашь мне право видеть твой канал?', delete_after=60)
                return False

            if not permissions.speak:
                await ctx.reply('Еще раз и я буду бороться за право голоса в этом голосовом канале!', delete_after=60)
                return False

            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
            return True
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.reply('Ты не в моем голосовом канале!', delete_after=60)
                return False
            else:
                return True

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            return await guild.voice_client.disconnect(force=True)
        if isinstance(event, lavalink.events.TrackStartEvent):
            ctx_player = event.player.fetch('channel')
            if ctx_player:
                ctx = self.bot.get_channel(ctx_player)
                if ctx:
                    embed = Embed(title='Сейчас играет', colour=0x2F3136, description='')
                    embed.description += f'[{event.track.title}]({event.track.uri})'
                    return await ctx.send(embed=embed, delete_after=event.track.duration/1000+60, view=PlayView(bot=self.bot, timeout=event.track.duration/1000+60))
        if isinstance(event, lavalink.events.WebSocketClosedEvent):
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            if guild.voice_client and event.reason == 'Disconnected.':
                await event.player.stop()
                return await guild.voice_client.fix_voice_state()

    @commands.command(aliases=['p'])
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, query: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip('<>')

        if not RURL.match(query) and not SPOTIFY_RURL.match(query):
            tracks = []
            tracks.append(query)
        elif SPOTIFY_RURL.match(query):
            data = SPOTIFY_RURL.match(query)
            tracks = await self.bot.loop.run_in_executor(None, partial(get_tracks, data.group('type'), data.group('id')))
        else:
            tracks = []
            tracks.append(query)
        
        async for i in AFor_Iter(tracks):
            _search = f'ytsearch:{i}'
            results = await player.node.get_tracks(_search)
            if not results or not results['tracks']:
                continue
            track = lavalink.models.AudioTrack(results['tracks'][0], ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)
            if not player.is_playing:
                await player.play()

        return await ctx.reply('Окей, я вроде нашёл эти пластинки...', delete_after=60)

    @commands.command(name='queue', aliases=['q'])
    @commands.guild_only()
    async def get_queue(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return

        if len(player.queue) == 0:
            return await ctx.reply('Сейчас тут пусто...', delete_after=60)

        embed = Embed(title='Очередь', description='', colour=0x2F3136)

        count = 1

        async for i in AFor_Iter(player.queue[:30]):
            embed.description += f'{count}. [{i.title}]({i.uri})\n'
            count += 1

        return await ctx.send(embed=embed, delete_after=60)

    @commands.command(aliases=['dc', 'leave'])
    @commands.guild_only()
    async def disconnect(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.send('Всем спасибо за вечеринку! До скорого!', delete_after=60)

    @commands.command(name='skip', aliases=['s'])
    @commands.guild_only()
    async def skip_track(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.reply('Пожалуйста, включи музыку для начала!', delete_after=60)

        await player.skip()
        return await ctx.reply('Окей, выключаю эту песню и начинаю играть новую!', delete_after=60)

    @commands.command(name='seek', description='Позволяет перемотать время трека на нужное кол-во секунд. Можно отмотать назад')
    @commands.guild_only()
    async def seek_track(self, ctx: commands.Context, time: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing or player.track.stream:
            return await ctx.reply('Извини, но ты просишь сделать невозможное!', delete_after=60)

        await player.seek(player.position+time*1000)
        return await ctx.reply('Без проблем. Сделано!', delete_after=60)

    @commands.command(name='shuffle', description='Перемешивает все следующие песни между собой')
    @commands.guild_only()
    async def shuffle_queue(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if len(player.queue) == 0 or not player.is_playing:
            return await ctx.reply('Ага. Может сначала закажешь музыку?', delete_after=60)

        player.shuffle = not player.shuffle
        return await ctx.reply('Окей. Я ' + ('' if player.shuffle else 'не ') + 'перемешиваю все следующие песни!', delete_after=60)

def setup(bot):
    bot.add_cog(Music(bot))