from discord.ext import commands, tasks
from utils.a_classes import AFor_Iter    

class Futures(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot 
        self.check_voice_state.start()
        self.send_statistic.start()

    @tasks.loop(minutes=15)
    async def check_voice_state(self):
        async for i in AFor_Iter(self.bot.voice_clients):
            if len(i.channel.members) < 2:
                await i.disconnect(force=True)

    @tasks.loop(hours=12)
    async def send_statistic(self):
        users = await self.bot.fetch_channel(917888203225169961)
        await users.edit(name=f'Users: {len(self.bot.users)}')
        guilds = await self.bot.fetch_channel(917888232933433365)
        await guilds.edit(name=f'Guilds: {len(self.bot.guilds)}')

def setup(bot):
    bot.add_cog(Futures(bot))