import asyncio
import datetime
import discord
import inspect
import os
import platform
import psutil

from .utils.checks import getAvi, getUser, me, perms
from .utils import config
from discord.ext import commands


class Tools:

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('config.json')
        self.logging = config.Config('log.json')

    # Command usage stats
    @commands.command()
    async def cmdstats(self, ctx):
        await ctx.message.delete()
        p = commands.Paginator()
        counter = self.bot.commands_triggered
        width = len(max(counter, key=len))
        total = sum(counter.values())
        fmt = '{0:<{width}}: {1}'
        p.add_line(fmt.format('Total', total, width=width))
        for key, count in counter.most_common():
            p.add_line(fmt.format(key, count, width=width))
        for page in p.pages:
            await ctx.send(page, delete_after=20)

    # Ping Time
    @commands.command()
    async def ping(self, ctx):
        msgTime = ctx.message.created_at
        await ctx.message.delete()
        now = datetime.datetime.now()
        ping = now - msgTime
        if perms(ctx.message):
            pong = discord.Embed(title='Pong!', colour=0x9b59b6)
            pong.add_field(name="Response Time:", value='%sms' % str(ping.total_seconds())[2:-3])
            pong.set_thumbnail(url='http://i.imgur.com/SKEmkvf.png')
            await ctx.send(embed=pong, delete_after=5)
        else:
            await ctx.send('**Pong!** - %sms' % str(ping.total_seconds())[2:-3], delete_after=5)

    # Time Since Bot is running
    @commands.command()
    async def uptime(self, ctx):
        delta = datetime.datetime.now() - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        fmt = '{h}h {m}m {s}s'
        if days:
            fmt = '{d}d ' + fmt
        embed = discord.Embed(title='\N{CLOCK FACE THREE OCLOCK} UPTIME', colour=0x9b59b6)
        embed.add_field(name='﻿ ', value=fmt.format(d=days, h=hours, m=minutes, s=seconds), inline=False)
        embed.set_thumbnail(url='http://i.imgur.com/mfxd06f.gif')
        if perms(ctx.message):
            await ctx.send(embed=embed, delete_after=10)
        else:
            await ctx.send('**Uptime:** %s' % fmt.format(d=days, h=hours, m=minutes, s=seconds), delete_after=5)
        await ctx.message.delete()

    # Various stat about the bot since startup
    @commands.command()
    async def stats(self, ctx):
        unique_members = set(self.bot.get_all_members())
        unique_online = sum(1 for m in unique_members if m.status != discord.Status.offline)
        voice = 0
        text = 0
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.VoiceChannel):
                    voice += 1
                elif isinstance(channel, discord.TextChannel):
                    text += 1
        alll = text+voice
        delta = datetime.datetime.now() - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h} hours, {m} minutes, and {s} seconds'
        if perms(ctx.message):
            embed = discord.Embed(title='\N{ELECTRIC LIGHT BULB} Bot Info', colour=0x9b59b6)
            embed.add_field(name='\N{CLOCK FACE THREE OCLOCK} UPTIME', value=fmt.format(d=days, h=hours, m=minutes, s=seconds), inline=False)
            embed.add_field(name='\N{SPEECH BALLOON} Commands Used', value=sum(self.bot.commands_triggered.values()), inline=True)
            embed.add_field(name='\N{INBOX TRAY} Messages Received', value=(self.bot.message_count - self.bot.icount), inline=True)
            embed.add_field(name='\N{OUTBOX TRAY} Messages Sent', value=self.bot.icount, inline=True)
            embed.add_field(name='\N{SPEAKING HEAD IN SILHOUETTE} Members [%s]' % len(unique_members), value='%s Online' % unique_online, inline=True)
            embed.add_field(name='\N{SPIRAL NOTE PAD} Channels [%s]' % alll, value='%s Text | %s Voice' % (text, voice), inline=True)
            embed.add_field(name='\N{TICKET} Guilds', value=len(self.bot.guilds))
            embed.add_field(name='\N{BELL} Mentions [%s]' % (self.bot.mention_count + self.bot.mention_count_name), value='%s Pings | %s Names' % (self.bot.mention_count, self.bot.mention_count_name), inline=True)
            try:
                embed.add_field(name='\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS} Most Used', value='%s [%s]' % (self.bot.commands_triggered.most_common()[0][0], self.bot.commands_triggered.most_common()[0][1]))
            except:
                embed.add_field(name='\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS} Most Used', value='﻿None')
            await ctx.send(embed=embed,  delete_after=20)
        else:
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)
        await ctx.message.delete()

    # Host System Infos
    @commands.command()
    async def sysinfo(self, ctx):
        embed = discord.Embed(title='\N{ELECTRIC LIGHT BULB} Host Info', colour=0x9b59b6)
        process = psutil.Process(os.getpid())
        t = datetime.datetime.fromtimestamp(int(process.create_time()))
        delta = datetime.datetime.now() - t
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        fmt = '{d}:{h}:{m}:{s}'
        memory_usage = process.memory_full_info().uss / 1024**2
        avai = psutil.virtual_memory().total / 1024**2
        mepro = process.memory_percent()
        prosys = psutil.cpu_percent()
        sys = '%s %s' % (platform.linux_distribution(full_distribution_name=1)[0].title(), platform.linux_distribution(full_distribution_name=1)[1])
        embed.add_field(name='\N{CLOCK FACE THREE OCLOCK} UPTIME', value=fmt.format(d=days, h=hours, m=minutes, s=seconds))
        embed.add_field(name='\N{DESKTOP COMPUTER} SYSTEM', value='{0}, {1}'.format(platform.system(), sys, platform.release()))
        embed.add_field(name='\N{FLOPPY DISK} MEMORY', value='{:.2f} MiB / {:.2f} MiB\nBot uses: {:.2f}%'.format(memory_usage, avai, mepro))
        embed.add_field(name='\N{DVD} CPU', value='{:.2f}%'.format(prosys))
        await ctx.message.delete()
        if perms(ctx.message):
            await ctx.send(embed=embed,  delete_after=20)
        else:
            await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)

    # Change Gamestatus - blank is no game
    @commands.command()
    async def game(self, ctx):
        """
        Changes Gamestatus
        """
        await self.config.put('gamestatus', ctx.message.content[6:])
        await ctx.message.delete()
        await ctx.send('Now playing: ``%s``' % self.config.get('gamestatus', []),  delete_after=5)

    # Find message with specific Text in Channel History...    Search Term(s) | Text
    @commands.command()
    async def quote(self, ctx):
        search = ctx.message.content[7:]
        content = ' '
        if '|' in ctx.message.content[7:]:
            msg = ctx.message.content[7:].split(" | ")
            search = msg[0]
            content = msg[1]
        async for message in ctx.message.channel.history(limit=500):
            if message.id != ctx.message.id:
                if search in message.content:
                    em = discord.Embed(description=message.clean_content, timestamp=message.created_at, colour=0x33CC66)
                    em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
                    await ctx.message.delete()
                    if perms(ctx.message):
                        await ctx.send(content=content, embed=em)
                    else:
                        await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} No Perms for Embeds, move to a better Guild!', delete_after=5)
                    return
        await ctx.message.delete()
        await ctx.send('Message not found!', delete_after=3)

    # Deletes messages from Channel History - only number for own, number and "all" to delete every message and not only the own
    @commands.command()
    async def clean(self, ctx, limit: int=25):
        msg_amt = 0
        async for message in ctx.message.channel.history(limit=limit):
                if me(message):
                    try:
                        await message.delete()
                    except:
                        pass
                    await asyncio.sleep(0.25)
                    msg_amt += 1
                elif ctx.message.content.endswith('all') and ctx.message.author.permissions_in(ctx.message.channel).manage_messages:
                    try:
                        await message.delete()
                    except:
                        pass
                    await asyncio.sleep(0.25)
                    msg_amt += 1
        await ctx.send('Cleaned `{}` messages out of `{}` that were checked.'.format(msg_amt, limit), delete_after=3)

    # DEBUG
    @commands.command()
    async def debug(self, ctx, *, code: str):
        await ctx.message.delete()
        code = code.strip('` ')
        python = '```ocaml\n>>> Input: {}\n{}\n```'
        result = None
        env = {
            'bot': self.bot,
            'say': ctx.send,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.message.guild,
            'server': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'self': self,
            'user': getUser,
            'avi': getAvi,
            }
        env.update(globals())
        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(python.format(code, '>>> %s' % type(e).__name__ + ': ' + str(e)))
            return
        await ctx.send(python.format(code, '>>> Output: %s' % result))


def setup(bot):
    bot.add_cog(Tools(bot))
