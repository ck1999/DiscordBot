from discord import ui, ButtonStyle, Interaction, Embed
from discord.ext import commands
from typing import List
from .a_classes import AFor_Iter
from discord.utils import get as __get__

#######################################################################################################################
#                                                       RACE                                                          #
#######################################################################################################################

class RaceButton(ui.Button["Race"]):
    def __init__(self, x: int, y: int, bid: int):
        super().__init__(style=ButtonStyle.secondary, label=f'№{x}', row=y)
        self.bid = bid

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: Race = self.view

        if interaction.user in view.players:
            return await interaction.response.send_message('Извиняй, но ставка уже сделана. Вернуть что-либо уже нельзя!', ephemeral=True)

        view.players[interaction.user] = self.label[1]

        players_text = ''
        for i in view.players.keys():
            players_text += f'{i.mention} - {view.players.get(i)}\n'

        return await interaction.response.edit_message(content=f'Ставьте на нужный номер!\nМы скоро начнем!\n\n{players_text}', view=view)

class Race(ui.View):

    children: List[RaceButton]

    def __init__(self, bid, started, timeout):
        super().__init__(timeout=timeout)

        self.bid = bid
        self.started = started
        self.players = {}

        for i in range(9):
            self.add_item(RaceButton(x=i+1, y=i//3, bid=bid))

    async def game(self, horse: int, ctx: commands.Context):
        winners = []
        for i in self.players.keys():
            if int(self.players.get(i)) == horse:
                winners.append(i)
                await ctx.reply(f'Есть победитель! {i.mention}, поздравляем. Ты поставил на лощадь {horse} и был абсолютно прав!')
        if not winners: return await ctx.reply(f'Нет победителей! Выиграла лошадь {horse}')

#######################################################################################################################
#                                                       MUSIC                                                         #
#######################################################################################################################

class PlayView(ui.View):

    def __init__(self, *, bot, timeout):
        super().__init__(timeout=timeout)

        self.bot = bot

    @ui.button(label='Skip', style=ButtonStyle.red)
    async def skip(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if not player.is_connected:
            return await interaction.response.send_message('Я и так не в голосовом канале...', ephemeral=True)

        if not interaction.user.voice or (player.is_connected and interaction.user.voice.channel.id != int(player.channel_id)):
            return await interaction.response.send_message('Для начала было бы неплохо зайти ко мне...', ephemeral=True)

        await player.skip()
        return await interaction.message.delete()

    @ui.button(label='Pause', style=ButtonStyle.gray)
    async def pause(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if not player.is_connected:
            return await interaction.response.send_message('Я и так не в голосовом канале...', ephemeral=True)

        if not interaction.user.voice or (player.is_connected and interaction.user.voice.channel.id != int(player.channel_id)):
            return await interaction.response.send_message('Для начала было бы неплохо зайти ко мне...', ephemeral=True)

        return await player.set_pause(True)

    @ui.button(label='Resume', style=ButtonStyle.gray)
    async def resume(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if not player.is_connected:
            return await interaction.response.send_message('Я и так не в голосовом канале...', ephemeral=True)

        if not interaction.user.voice or (player.is_connected and interaction.user.voice.channel.id != int(player.channel_id)):
            return await interaction.response.send_message('Для начала было бы неплохо зайти ко мне...', ephemeral=True)

        return await player.set_pause(False)

    @ui.button(label='Queue', style=ButtonStyle.gray)
    async def get_queue(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if len(player.queue) == 0:
            return await interaction.response.send_message('Сейчас тут пусто...', ephemeral=True)

        embed = Embed(title='Очередь', description='', colour=0x2F3136)

        count = 1

        for i in player.queue[:30]:
            embed.description += f'{count}. [{i.title}]({i.uri})\n'
            count += 1

        return await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label='Repeat', style=ButtonStyle.gray)
    async def repeating_music(self, button: ui.Button, interaction: Interaction):

        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if not player.is_connected:
            return await interaction.response.send_message('Я и так не в голосовом канале...', ephemeral=True)

        if not interaction.user.voice or (player.is_connected and interaction.user.voice.channel.id != int(player.channel_id)):
            return await interaction.response.send_message('Для начала было бы неплохо зайти ко мне...', ephemeral=True)

        player.repeat = not player.repeat
        if player.repeat:
            return await interaction.response.send_message('Окей. Теперь я буду повторять эту песню вечно!', ephemeral=True)
        else:
            return await interaction.response.send_message('Без проблем. Мне уже самому надоело...', ephemeral=True)

#######################################################################################################################
#                                                 Custom Roles                                                        #
#######################################################################################################################
class CustomRolesButton(ui.Button["CRV"]):
    def __init__(self, role, text, custom_id):
        super().__init__(style=ButtonStyle.secondary, label=f'{text}', custom_id=custom_id)
        self.role = role

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        assert self.role.position < interaction.message.author.top_role.position
        assert interaction.message.author.guild_permissions.administrator == True

        if interaction.user.get_role(self.role.id):
            await interaction.user.remove_roles(self.role)
            return await interaction.response.send_message('123', ephemeral=True)
        else:
            await interaction.user.add_roles(self.role)
            return await interaction.response.send_message('456', ephemeral=True)

class CRV(ui.View):

    children: List[CustomRolesButton]

    def __init__(self):
        super().__init__(timeout=None)

    async def crv_add(self, role, text, custom_id):
        button = CustomRolesButton(role, text, custom_id)
        self.add_item(button)

    # async def crd_remove(self, role):
    #     self.roles.pop(role.id)
    #     async for key in AFor_Iter(self.roles.keys()):
    #         custom_id = self.roles.get(key)
    #         text = 
    #         button = CustomRolesButton(, text, custom_id)
        # self.roles.index()
        # obj = (role.id,)
        # self.roles.remove()