import discord, json, datetime
from discord.ext import commands

async def open_json(name):
    with open(name, 'r') as f:
        return json.load(f)

class Logs(commands.Cog, name='Logs'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        path = 'cogs/json_data/{}/guild.json'.format(guild.id)
        guild_info = await open_json(path)
        try:
            log_channel = await self.bot.fetch_channel(guild_info["main"]['log'])
        except:
            return 0
        embed = discord.Embed(title="Участника забанили", timestamp=datetime.datetime.utcnow())
        embed.add_field(name=f'Nickname:', value=f'{member.mention}')
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'ID: {member.id}')
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        path = 'cogs/json_data/{}/guild.json'.format(guild.id)
        guild_info = await open_json(path)
        try:
            log_channel = await self.bot.fetch_channel(guild_info["main"]['log'])
        except:
            return 0
        embed = discord.Embed(title=f"Пользователя {member.mention} разбанили", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'ID: {member.id}')
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        path = 'cogs/json_data/{}/guild.json'.format(member.guild.id)
        guild_info = await open_json(path)
        try:
            log_channel = await self.bot.fetch_channel(guild_info["main"]['log'])
        except:
            return 0
        embed = discord.Embed(title=f"Пользователь {member} покинул сервер", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'ID: {member.id}')
        await log_channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        path = 'cogs/json_data/{}/guild.json'.format(member.guild.id)
        guild_info = await open_json(path)
        try:
            log_channel = await self.bot.fetch_channel(guild_info["main"]['log'])
        except:
            return 0
        embed = discord.Embed(title=f"Пользователь {member} зашел на сервер", timestamp=datetime.datetime.utcnow())
        embed.add_field(name=f'Created at: ', value=member.created_at)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f'ID: {member.id}')
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        path = 'cogs/json_data/{}/guild.json'.format(channel.guild.id)
        guild_info = await open_json(path)
        try:
            log_channel = await self.bot.fetch_channel(guild_info["main"]['log'])
        except:
            return 0
        embed = discord.Embed(title="Создан новый канал", timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Name:", value=channel.name, inline = True)
        try:
            embed.add_field(name="Region:", value=channel.rtc_region, inline = True)
            embed.add_field(name="Limit:", value=channel.user_limit, inline = True)
            embed.add_field(name="Bitrate:", value=channel.bitrate, inline = True)
            embed.add_field(name="Guild:", value=channel.guild.name, inline = True)
        except:
            pass
        embed.add_field(name="Type:", value=channel.type, inline = True)
        embed.set_footer(text=f'ID: {channel.id}')
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        path = 'cogs/json_data/{}/guild.json'.format(channel.guild.id)
        guild_info = await open_json(path)
        try:
            log_channel = await self.bot.fetch_channel(guild_info["main"]['log'])
        except:
            return 0
        embed = discord.Embed(title="Канал удален", timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Channel name:", value=channel.name, inline=True)
        embed.add_field(name="Type:", value=channel.type, inline = True)
        embed.set_footer(text=f'ID: {channel.id}')
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_private_channel_create(self, channel):
        path = 'cogs/json_data/{}/guild.json'.format(channel.guild.id)
        guild_info = await open_json(path)
        try:
            log_channel = await self.bot.fetch_channel(guild_info["main"]['log'])
        except:
            return 0
        embed = discord.Embed(title="Создан новый приватный канал", timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Name:", value=channel.name, inline = True)
        try:
            embed.add_field(name="Region:", value=channel.rtc_region, inline = True)
            embed.add_field(name="Limit:", value=channel.user_limit, inline = True)
            embed.add_field(name="Bitrate:", value=channel.bitrate, inline = True)
            embed.add_field(name="Guild:", value=channel.guild.name, inline = True)
        except:
            pass
        embed.add_field(name="Type:", value=channel.type, inline = True)
        embed.set_footer(text=f'ID: {channel.id}')
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_private_channel_delete(self, channel):
        path = 'cogs/json_data/{}/guild.json'.format(channel.guild.id)
        guild_info = await open_json(path)
        try:
            log_channel = await self.bot.fetch_channel(guild_info["main"]['log'])
        except:
            return 0
        embed = discord.Embed(title="Приватный канал удален", timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Channel name:", value=channel.name, inline=True)
        embed.add_field(name="Type:", value=channel.type, inline = True)
        embed.set_footer(text=f'ID: {channel.id}')
        await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logs(bot))