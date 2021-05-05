import discord, asyncio
from discord.ext import commands

class NotAnAdmin(commands.CheckFailure):
    pass

class NoKickPerm(commands.CheckFailure):
    pass

class NoBanPerm(commands.CheckFailure):
    pass

def is_admin():
    async def predicate(ctx):
        for role in ctx.author.roles:
            if role.permissions.administrator:
                return True
        raise NotAnAdmin('Ты не админ!')
    return commands.check(predicate)

def can_kick():
    async def predicate(ctx):
        for role in ctx.author.roles:
            if role.permissions.administrator or role.permissions.kick_members:
                return True
        raise NoKickPerm('У тебя нет прав кикать пользователей!')
    return commands.check(predicate)

def can_ban():
    async def predicate(ctx):
        for role in ctx.author.roles:
            if role.permissions.administrator or role.permissions.ban_members:
                return True
        raise NoBanPerm('У тебя нет прав банить пользователей!')
    return commands.check(predicate)
