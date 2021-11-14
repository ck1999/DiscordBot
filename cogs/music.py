from re import compile
import asyncio
import lavalink, requests
from discord.ext import commands
from discord import abc, VoiceClient, Client, Embed, ui, ButtonStyle, Interaction
import spotipy as s
from spotipy.oauth2 import SpotifyClientCredentials
from .settings import settings, spotify_settings

spoti = s.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotify_settings.get('client_id'), client_secret=spotify_settings.get('client_secret')))

url_rx = compile(r'https?://(?:www\.)?.+')

class PlayView(ui.View):

    def __init__(self, *, bot, timeout):
        super().__init__(timeout=timeout)

        self.bot = bot

    @ui.button(label='Skip', style=ButtonStyle.red)
    async def skip(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if not player.is_connected:
            return await interaction.response.send_message('Я и так не в голосовом канале...', ephemeral=True)

        if not interaction.message.author.voice or (player.is_connected and interaction.message.author.voice.channel.id != int(player.channel_id)):
            return await interaction.response.send_message('Для начала было бы неплохо зайти ко мне...', ephemeral=True)

        await player.skip()
        return await interaction.message.delete()

    @ui.button(label='Pause', style=ButtonStyle.gray)
    async def pause(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if not player.is_connected:
            return await interaction.response.send_message('Я и так не в голосовом канале...', ephemeral=True)

        if not interaction.message.author.voice or (player.is_connected and interaction.message.author.voice.channel.id != int(player.channel_id)):
            return await interaction.response.send_message('Для начала было бы неплохо зайти ко мне...', ephemeral=True)

        return await player.set_pause(True)

    @ui.button(label='Resume', style=ButtonStyle.gray)
    async def resume(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if not player.is_connected:
            return await interaction.response.send_message('Я и так не в голосовом канале...', ephemeral=True)

        if not interaction.message.author.voice or (player.is_connected and interaction.message.author.voice.channel.id != int(player.channel_id)):
            return await interaction.response.send_message('Для начала было бы неплохо зайти ко мне...', ephemeral=True)

        return await player.set_pause(False)

    @ui.button(label='Queue', style=ButtonStyle.gray)
    async def get_queue(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if len(player.queue) == 0:
            return await interaction.response.send_message('Сейчас тут пусто...', ephemeral=True)

        embed = Embed(title='Очередь', description='', colour=0x2F3136)

        count = 1

        for i in player.queue:
            embed.description += f'{count}. [{i.title}]({i.uri})\n'
            count += 1

        return await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label='Repeat', style=ButtonStyle.gray)
    async def repeating_music(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if not player.is_connected:
            return await interaction.response.send_message('Я и так не в голосовом канале...', ephemeral=True)

        if not interaction.message.author.voice or (player.is_connected and interaction.message.author.voice.channel.id != int(player.channel_id)):
            return await interaction.response.send_message('Для начала было бы неплохо зайти ко мне...', ephemeral=True)

        player.repeat = not player.repeat
        if player.repeat:
            return await interaction.response.send_message('Окей. Теперь я буду повторять эту песню вечно!', ephemeral=True)
        else:
            return await interaction.response.send_message('Без проблем. Мне уже самому надоело...', ephemeral=True)

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

    async def disconnect(self, *, force: bool) -> None:

        player = self.lavalink.player_manager.get(self.channel.guild.id)

        if not force and not player.is_connected:
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

    async def cog_before_invoke(self, ctx: commands.Context):
        guild_check = ctx.guild is not None

        if guild_check:
            await self.ensure_voice(ctx)

        return guild_check

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandInvokeError):
            return await ctx.send(error.original)

    async def ensure_voice(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply('Сначала зайди в любой голосовой канал!')

        if not player.is_connected:

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect:
                return await ctx.reply('Извини, но я не вижу куда заходить. Может дашь мне право видеть?')

            if not permissions.speak:
                return await ctx.reply('Еще раз и я буду бороться за право голоса в этом голосовом канале!')

            player.store('channel', ctx.channel.id)
            return await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                return await ctx.reply('Ты не в моем голосовом канале!')

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
                    return await ctx.send(embed=embed, delete_after=event.track.duration/1000+60, view=PlayView(bot=self.bot, timeout=event.track.duration/1000))
        if isinstance(event, lavalink.events.WebSocketClosedEvent):
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            if guild.voice_client and event.reason == 'Disconnected.':
                await event.player.stop()
                return await guild.voice_client.fix_voice_state()

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context, *, query: str):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_music'):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        if 'spotify' in query:
            if 'playlist' in query:
                response = spoti.playlist_items(query, fields='items.track.id')
                tracks = []
                for i in response.get('items'):
                    track = spoti.track(i.get('track').get('id'))
                    tracks.append(track.get('name') + ' ' + track.get('artists')[0].get('name'))
                
                for track_name in tracks:
                    query = f'ytsearch:{track_name}'
                    results = await player.node.get_tracks(query)
                    if not results or not results['tracks']:
                        pass
                    else:
                        _track = results['tracks'][0]
                        player.add(requester=ctx.author.id, track=_track)

                embed = Embed(color=0x2F3136)
                embed.title = 'Плейлист добавлен!'
                embed.description = f'Песен добавлено: {len(tracks)}'
            elif 'album' in query:
                response = spoti.album(query)
                query = response.get('name') + ' ' + response.get('artists')[0].get('name') + ' album '
                query = f'ytsearch:{query}'
                results = await player.node.get_tracks(query)
                if not results or not results['tracks']:
                        pass
                else:
                    _track = results['tracks'][0]
                    player.add(requester=ctx.author.id, track=_track)
                embed = Embed(color=0x2F3136)
                embed.title = 'Альбом добавлен!'
                embed.description = f'[{_track["info"]["title"]}]({_track["info"]["uri"]})'
            elif 'track' in query:
                response = spoti.track(query)
                query = response.get('name') + ' ' + response.get('artists')[0].get('name') + ' song '
                query = f'ytsearch:{query}'
                results = await player.node.get_tracks(query)
                if not results or not results['tracks']:
                        pass
                else:
                    _track = results['tracks'][0]
                    player.add(requester=ctx.author.id, track=_track)
                embed = Embed(color=0x2F3136)
                embed.title = 'Песня добавлена!'
                embed.description = f'[{_track["info"]["title"]}]({_track["info"]["uri"]})'
            else:
                embed = Embed(color=0x2F3136)
                embed.title = 'Возникла ошибка'
                embed.description = f'Если вы считаете, что бот неправ, то\nОтправьте тикет в поддержку: >ticket'
        else:
            results = await player.node.get_tracks(query)

            if not results or not results['tracks']:
                return await ctx.send('Ничего не найдено!')

            embed = Embed(color=0x2F3136)

            # Valid loadTypes are:
            #   TRACK_LOADED    - single video/direct URL)
            #   PLAYLIST_LOADED - direct URL to playlist)
            #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
            #   NO_MATCHES      - query yielded no results
            #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
            if results['loadType'] == 'PLAYLIST_LOADED':
                tracks = results['tracks']

                for track in tracks:
                    player.add(requester=ctx.author.id, track=track)

                embed.title = 'Плейлист добавлен!'
                embed.description = f'{results["playlistInfo"]["name"]}\nВсего песен: {len(tracks)}'
            else:
                track = results['tracks'][0]
                embed.title = 'Песня добавлена!'
                embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

                track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
                player.add(requester=ctx.author.id, track=track)

        if player.is_playing:
            await ctx.send(embed=embed, delete_after=300)

        if not player.is_playing:
            await player.play()

    @commands.command(name='queue', aliases=['q'])
    async def get_queue(self, ctx: commands.Context):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_music'):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if len(player.queue) == 0:
            return await ctx.reply('Сейчас тут пусто...')

        embed = Embed(title='Очередь', description='', colour=0x2F3136)

        count = 1

        for i in player.queue[:30]:
            embed.description += f'{count}. [{i.title}]({i.uri})\n'
            count += 1

        return await ctx.send(embed=embed)

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx: commands.Context):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_music'):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.send('Всем спасибо за вечеринку! До скорого!')

    @commands.command(name='skip', aliases=['s'])
    async def skipping(self, ctx: commands.Context):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_music'):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return

        await player.skip()
        return await ctx.reply('Окей, выключаю эту песню и начинаю играть новую!')

    @commands.command(name='seek', description='Позволяет перемотать время трека на нужное кол-во секунд. Можно отмотать назад')
    async def seek_track(self, ctx: commands.Context, time: int = 10):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_music'):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return

        await player.seek(player.position+time*1000)
        return await ctx.reply('Без проблем. Сделано!')

    @commands.command(name='shuffle', description='Перемешивает все следующие песни между собой')
    async def shuffle_queue(self, ctx: commands.Context):
        request = requests.get(settings.get('api')+f'guilds/{ctx.guild.id}')
        if not request.json().get('setting_plugin_music'):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return

        player.shuffle = not player.shuffle
        return await ctx.reply('Окей. Я ' + ('' if player.shuffle else 'не ') + 'перемешиваю все следующие песни!')

def setup(bot):
    bot.add_cog(Music(bot))