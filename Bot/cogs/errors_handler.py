from discord.ext import commands
from time import strftime, gmtime

class ErrorsHandler(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
        self.y = '\<y:907808729028780062>'
        self.x = '\<x:907808728898756608>'
        self.n = '\<no:907985288633139210>'

    @commands.Cog.listener()
    async def on_command_error(self, object, error):
        if isinstance(error, commands.CommandOnCooldown):
            beauty = strftime("%Hч %Mм %Sс", gmtime(error.retry_after))
            return await object.reply(f'Не торопись, ковбой! Подожди еще `{beauty}`', delete_after=300)
        if isinstance(error, commands.CommandNotFound):
            return await object.reply('Ты перепутал бота, дружок!', delete_after=300)
        if isinstance(error, commands.UserNotFound):
            return print(f'{object.author.name} -> {error.argument}')
        if isinstance(error, commands.DisabledCommand):
            return await object.reply('Пока что команда выключена. Мы ее обязательно вернем!', delete_after=300)
        if isinstance(error, commands.MessageNotFound):
            return
        if isinstance(error, commands.MemberNotFound):
            return await object.reply('Прости, но я не могу найти такого пользователя в своей переписи населения. Ты уверен, что мы с ним знакомы?', delete_after=300)
        if isinstance(error, commands.MissingPermissions):
            return
        if isinstance(error, commands.NotOwner):
            return await object.message.add_reaction(self.n)
        if isinstance(error, commands.NoPrivateMessage):
            return await object.reply('Извини, но эту команду можно использовать только на серверах...', delete_after=300)
        if isinstance(error, commands.CommandInvokeError):
            print(error)
        if isinstance(error, commands.CheckFailure):
            return
        try:
            data = await self.bot.connector.get_data(f'guilds/{object.guild.id}')
            prefix = data.get('prefix')
        except AttributeError:
            prefix = '!'
        if isinstance(error, commands.MissingRequiredArgument):
            return await object.reply(f'Ты забыл добавить параметры в команду.\nПропиши `{prefix}help [Command]`, если у тебя есть вопросы', delete_after=300)
        print('----------------------------------------------------------------')
        try:
            await object.message.add_reaction(self.x)
            await object.reply(f'Произошло недоразумение. Сделайте тикет в тех. поддержку, если такое повторяется постоянно\nТикет можно отправить в личные сообщения боту\nОтправить тикет: {prefix}ticket', delete_after=300)
        except:
            pass
        raise error

def setup(bot):
    bot.add_cog(ErrorsHandler(bot))