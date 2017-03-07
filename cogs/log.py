import discord
import logging

from discord.ext import commands
from .utils import config
from .utils.checks import getUser, perms

log = logging.getLogger('LOG')


class Logging:

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('config.json')
        self.logging = config.Config('log.json')

    # Log Help
    @commands.group()
    async def log(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.message.delete()
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} ``on``, ``off``, ``status``, ``key <word>``, ``block <word>``, ``show``, ``blacklist guild``, ``blacklist channel`` or ``blacklist user <user>``', delete_after=5)

    # Log On
    @log.command()
    async def on(self, ctx):
        await self.config.put('setlog', 'on')
        await ctx.message.delete()
        await ctx.send('\N{HEAVY CHECK MARK} Mention Log set to ``on``', delete_after=3)

    # Log Off
    @log.command()
    async def off(self, ctx):
        await self.config.put('setlog', 'off')
        await ctx.message.delete()
        await ctx.send('\N{HEAVY CHECK MARK} Mention Log set to ``off``', delete_after=3)

    # Log Status
    @log.command()
    async def status(self, ctx):
        await ctx.message.delete()
        await ctx.send('<:robot:273922151856209923> Mention logging is currently ``%s``' % self.config.get('setlog', []), delete_after=3)

    # Add Key-Word to Logger
    @log.command()
    async def key(self, ctx, msg: str):
        await ctx.message.delete()
        msg = msg.lower()
        keys = self.logging.get('key', {})
        if msg in keys:
            keys.remove(msg)
            await self.logging.put('key', keys)
            await ctx.send('\N{HEAVY CHECK MARK} Removed Keyword ``%s`` from Logger' % msg,  delete_after=5)
        elif msg not in keys:
            keys.append(msg)
            await self.logging.put('key', keys)
            await ctx.send('\N{HEAVY CHECK MARK} Added Keyword ``%s`` to Logger' % msg,  delete_after=5)

    # Add Blocked-Key-Word to Logger
    @log.command()
    async def block(self, ctx, msg: str):
        await ctx.message.delete()
        msg = msg.lower()
        keys = self.logging.get('key-blocked', {})
        if msg in keys:
            keys.remove(msg)
            await self.logging.put('key-blocked', keys)
            await ctx.send('\N{HEAVY CHECK MARK} Unblocked ``%s`` from Logger' % msg,  delete_after=5)
        elif msg not in keys:
            keys.append(msg)
            await self.logging.put('key-blocked', keys)
            await ctx.send('\N{HEAVY CHECK MARK} Blocked ``%s`` from Logger' % msg,  delete_after=5)

    # Show Logging Infosconfig
    @log.command()
    async def show(self, ctx):
        await ctx.message.delete()
        em = discord.Embed(title='Logging Info', colour=0x9b59b6)

        keys = ', '.join(self.logging.get('key', {}))
        if keys is not '':
            em.add_field(name="Logged Words[%s] " % len(self.logging.get('key', {})), value=keys)

        blocked = ', '.join(self.logging.get('key-blocked', {}))
        if blocked is not '':
            em.add_field(name="Blocked Words[%s] " % len(self.logging.get('key-blocked', {})), value=blocked)

        guilds = ', '.join(str(self.bot.get_guild(i)) for i in self.logging.get('block-guild', {}))
        # I should rework that shit sometime
        if guilds is not '':
            if len(guilds) < 1024:
                em.add_field(name="Blocked Guilds[%s]" % len(self.logging.get('block-guild', {})), value=guilds, inline=False)
            else:
                temp = []
                first = True
                count = 1
                send = ''
                for i in guilds.split(', '):
                    if len(send + i + ', ') < 1024:
                        if count == len(guilds.split(', ')):
                            send += i + ', '
                            temp.append(send)
                        else:
                            send += i + ', '
                            count += 1
                    else:
                        temp.append(send)
                        send = i + ', '
                        count += 1
                for x in temp:
                    if first:
                        first = False
                        em.add_field(name="Blocked Guilds[%s]" % len(self.logging.get('block-guild', {})), value=x[:-2], inline=False)
                    else:
                        em.add_field(name=u"\u2063", value=x[:-2], inline=False)

        users = ', '.join(str(u) for u in self.bot.users if u.id in self.logging.get('block-user', {}))
        if users is not '':
            em.add_field(name="Blocked Users[%s]" % len(self.logging.get('block-user', {})), value=users, inline=False)

        channel = ', '.join(str(self.bot.get_channel(i)) for i in self.logging.get('block-channel', {}))
        if channel is not '':
            em.add_field(name="Blocked Channels[%s]" % len(self.logging.get('block-channel', {})), value=channel, inline=False)

        if perms(ctx.message):
            await ctx.send(embed=em, delete_after=20)
        else:
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)

    # Blacklist "Help"
    @log.group(no_pm=True)
    async def blacklist(self, ctx):
        if ctx.message.content == '/log blacklist':
            await ctx.message.delete()
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} Use **FULL** command', delete_after=5)

    # Blacklist Guild
    @blacklist.command(no_pm=True)
    async def guild(self, ctx):
        await ctx.message.delete()
        guilds = self.logging.get('block-guild', {})
        guild = ctx.message.guild.id
        if guild in guilds:
            guilds.remove(guild)
            await self.logging.put('block-guild', guilds)
            await ctx.send('\N{HEAVY CHECK MARK} Removed guild with ID ``%s`` from blacklist' % guild,  delete_after=5)
        else:
            guilds.append(guild)
            await self.logging.put('block-guild', guilds)
            await ctx.send('\N{HEAVY CHECK MARK} Added guild with ID ``%s`` to blacklist' % guild,  delete_after=5)

    # Blacklist Channel
    @blacklist.command(no_pm=True)
    async def channel(self, ctx):
        await ctx.message.delete()
        channels = self.logging.get('block-channel', {})
        channel = ctx.message.channel.id
        if channel in channels:
            channels.remove(channel)
            await self.logging.put('block-channel', channels)
            await ctx.send('\N{HEAVY CHECK MARK} Removed Channel with ID ``%s`` from blacklist' % channel,  delete_after=5)
        else:
            channels.append(channel)
            await self.logging.put('block-channel', channels)
            await ctx.send('\N{HEAVY CHECK MARK} Added Channel with ID ``%s`` to blacklist' % channel,  delete_after=5)

    # Blacklist user
    @blacklist.command(no_pm=True)
    async def user(self, ctx, msg: str):
        await ctx.message.delete()
        users = self.logging.get('block-user', {})
        user = getUser(ctx.message, msg)
        if not user:
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} User not found',  delete_after=5)
            return
        if user.id in users:
            users.remove(user.id)
            await self.logging.put('block-user', users)
            await ctx.send('\N{HEAVY CHECK MARK} Removed %s with ID ``%s`` from blacklist' % (ctx.message.guild.get_member(user.id), user.id),  delete_after=5)
        else:
            users.append(user.id)
            await self.logging.put('block-user', users)
            await ctx.send('\N{HEAVY CHECK MARK} Added %s with ID ``%s`` to blacklist' % (ctx.message.guild.get_member(user.id), user.id),  delete_after=5)

    # Automatically remove channel and guilds from blacklist on leave
    async def on_guild_remove(self, guild):
        log.info('Left Guild "{}" '.format(guild.name))
        guilds = self.logging.get('block-guild', [])
        if guild.id in guilds:
            guilds.remove(guild.id)
            await self.logging.put('block-guild', guilds)
            log.info('Removed Guild "{}" on leave from blacklist'.format(guild.name))
        channels = self.logging.get('block-channel', [])
        for channel in guild.channels:
            if channel.id in channels:
                channels.remove(channel.id)
                await self.logging.put('block-channel', channels)
                log.info('Removed Channel "{}" in Guild "{}" on leave from blacklist'.format(channel.name, guild.name))

    # Automatically add guilds to blacklist on join
    async def on_guild_join(self, guild):
        log.info('Joined Guild "{}" '.format(guild.name))
        guilds = self.logging.get('block-guild', [])
        if guild.id not in guilds:
            guilds.append(guild.id)
            await self.logging.put('block-guild', guilds)
            log.info('Added Guild "{}" on join to blacklist'.format(guild.name))


def setup(bot):
    bot.add_cog(Logging(bot))
