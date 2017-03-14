import datetime
import discord
import logging
import time
import traceback

from cogs.utils import config
from collections import Counter
from discord.ext import commands

# "Database"
config = config.Config('config.json')

# Logging
log = logging.getLogger('LOG')
log.setLevel(logging.INFO)
if not log.handlers:
    handler = logging.FileHandler(filename='Logs/SelfIgneel' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.log', encoding='utf-8', mode='w')
    ch = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S:%s'))
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%H:%M:%S:%s'))
    log.addHandler(handler)
    log.addHandler(ch)
log.propagate = False

extensions = ['cogs.cmds',
              'cogs.cogs',
              'cogs.debug',
              'cogs.google',
              'cogs.info',
              'cogs.log',
              'cogs.mal',
              'cogs.misc',
              'cogs.msg',
              'cogs.tools'
              ]

bot = commands.Bot(command_prefix=config.get('prefix', []), description='''Selfbot''', self_bot=True)


# Startup
@bot.event
async def on_ready():
    log.info('------')
    log.info('Logged in as')
    log.info(str(bot.user) + '(' + str(bot.user.id) + ')')
    log.info('------')
    bot.uptime = datetime.datetime.now()
    bot.message_count = 0
    bot.commands_triggered = Counter()
    bot.icount = 0
    bot.mention_count = 0
    bot.mention_count_name = 0
    bot.refresh_time = time.time()
    if config.get('restart', []) == 'true':
        await config.put('restart', '')
        await bot.get_channel(config.get('restart_channel', [])).send(':wave: Back Running!', delete_after=2)


# Command Errors
@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.message.delete()
        await ctx.send('\N{HEAVY EXCLAMATION MARK SYMBOL} Only usable on Servers', delete_after=3)
    elif isinstance(error, commands.CommandNotFound):
        await ctx.message.delete()
        log.warning('{0.message.content} is an invalid command or usercommand!'.format(ctx))
        pass
    elif isinstance(error, commands.CommandInvokeError):
        log.error('In {0.command.qualified_name}:\n{1}'.format(ctx, ''.join(traceback.format_list(traceback.extract_tb(error.original.__traceback__)))))
        log.error('{0.__class__.__name__}: {0}'.format(error.original))


# Increase use count and log to logger
@bot.event
async def on_command_completion(ctx):
    bot.commands_triggered[ctx.command.qualified_name] += 1
    message = ctx.message
    destination = None
    if isinstance(message.channel, discord.DMChannel):
        destination = 'Private Message'
    else:
        destination = '#{0.channel.name},({0.guild.name})'.format(message)
    log.info('In {1}:{0.content}'.format(message, destination))

# Load Extensions / Logger / Runbot
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.warning('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
    bot.run(config.get('token', []), bot=False)
    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)
