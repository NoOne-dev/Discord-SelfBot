import discord
import logging
import datetime
from discord import utils
from .utils import config
from .utils.allmsgs import quickcmds, custom
from .utils.checks import hasPassed, perms, me, getAvi

log = logging.getLogger('LOG')


class OnMessage:
    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('config.json')
        self.logging = config.Config('log.json')

    async def on_message(self, message):
        # Increase Message Count
        if hasattr(self.bot, 'message_count'):
            self.bot.message_count += 1
        # Set GAmestatus/Onlinestatus every given time (60Sec default)
        if hasattr(self.bot, 'refresh_time'):
            if hasPassed(self.bot, self.bot.refresh_time):
                if self.config.get('gamestatus', []) == '':
                    await self.bot.change_presence(status='invisible', afk=True)
                else:
                    await self.bot.change_presence(game=discord.Game(name=self.config.get('gamestatus', [])), status='invisible', afk=True)
        # Custom commands
        if me(message):
            if hasattr(self.bot, 'icount'):
                self.bot.icount += 1
            prefix = False
            for i in self.config.get('prefix', []):
                if message.content.startswith(i):
                    prefix = True
                    break
            if prefix:
                response = custom(message.content)
                if response is None:
                    pass
                else:
                    if response[0] == 'embed':
                        if perms(message):
                            await message.channel.send(content='%s' % response[2], embed=discord.Embed(colour=0x9b59b6).set_image(url=response[1]))
                        else:
                            await message.channel.send('{0}\n{1}'.format(response[2], response[1]))
                    else:
                        await message.channel.send('{0}\n{1}'.format(response[2], response[1]))
                    self.bot.commands_triggered[response[3]] += 1
                    destination = None
                    if isinstance(message.channel, discord.DMChannel):
                        destination = 'Private Message'
                    else:
                        destination = '#{0.channel.name},({0.guild.name})'.format(message)
                    log.info('In {1}:{0.content}'.format(message, destination))
            else:
                response = quickcmds(message.content.lower().strip())
                if response:
                    await message.delete()
                    self.bot.commands_triggered[response[1]] += 1
                    await message.channel.send(response[0])
                    destination = None
                    if isinstance(message.channel, discord.DMChannel):
                        destination = 'Private Message'
                    else:
                        destination = '#{0.channel.name},({0.guild.name})'.format(message)
                    log.info('In {1}:{0.content}'.format(message, destination))
        elif (message.guild is not None) and (self.config.get('setlog', []) == 'on'):
            mention = name = ping = False
            if (message.guild.id not in self.logging.get('block-guild', [])) and (message.author.id not in self.logging.get('block-user', [])) or (message.channel.id not in self.logging.get('block-channel', [])):
                if (message.guild.get_member(self.config.get('me', [])).mentioned_in(message)):
                    em = discord.Embed(title='\N{BELL} MENTION', colour=0x9b59b6)
                    ping = True
                    role = False
                    if hasattr(self.bot, 'mention_count'):
                        self.bot.mention_count += 1
                    for role in message.role_mentions:
                        if utils.find(message.author.roles, id=role.id):
                            role = True
                            em = discord.Embed(title='\N{SPEAKER WITH THREE SOUND WAVES} ROLE MENTION', colour=0x9b59b6)
                            log.info("Role Mention from #%s, %s" % (message.channel, message.guild))
                    if not role:
                        log.info("Mention from #%s, %s" % (message.channel, message.guild))
                elif (not ping) and (not(any(map(lambda v: v in message.content.lower().split(), self.logging.get('key-blocked', []))))):
                    for word in self.logging.get('key', []):
                        if word in message.content.lower().split():
                            em = discord.Embed(title='\N{HEAVY EXCLAMATION MARK SYMBOL} %s MENTION' % word.upper(), colour=0x9b59b6)
                            mention = True
                            name = True
                            log.info("%s Mention in #%s, %s" % (word.title(), message.channel, message.guild))
                            break
                if mention or ping:
                    if name:
                        if hasattr(self.bot, 'mention_count_name'):
                            self.bot.mention_count_name += 1
                    em.set_author(name=message.author, icon_url=getAvi(message.author))
                    em.add_field(name='In', value="#%s, ``%s``" % (message.channel, message.guild), inline=False)
                    em.add_field(name='At', value="%s" % datetime.datetime.now().__format__('%A, %d. %B %Y @ %H:%M:%S'), inline=False)
                    em.add_field(name='Message', value="%s" % message.clean_content, inline=False)
                    em.set_thumbnail(url=getAvi(message.author))
                    await self.bot.get_channel(self.config.get('log_channel', [])).send(embed=em)


def setup(bot):
    bot.add_cog(OnMessage(bot))
