import datetime
import discord
import inspect
import io
import os
import pytz
import textwrap
import traceback

from .utils.checks import getUser
from .utils import config
from contextlib import redirect_stdout
from discord.ext import commands


class Debug:

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('config.json')
        self.logging = config.Config('log.json')
        self._last_result = None

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
            'discord': discord
            }
        env.update(globals())
        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(python.format(code, '>>> %s' % type(e).__name__ + ': ' + str(e)))
            return
        if len(str(code) + '>>> Output:' + str(result)) > 2000:
            time = datetime.datetime.now(pytz.timezone('CET'))
            result_file = 'result_%s_at_%s.txt' % (time.strftime('%x').replace('/', '_'), time.strftime('%X').replace(':', '_'))
            with open(result_file, 'w') as file:
                file.write(str(result))
            with open(result_file, 'rb') as file:
                await ctx.send(python.format(code, '>>> Output: See attached file!'), file=file)
            os.remove(result_file)
        else:
            await ctx.send(python.format(code, '>>> Output: %s' % result))

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return '```py\n{0.__class__.__name__}: {0}\n```'.format(e)
        return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

    # Eval Command
    @commands.command(name='eval')
    async def _eval(self, ctx, *, body: str):
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
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = 'async def func():\n%s' % textwrap.indent(body, '  ')

        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await ctx.send(self.get_syntax_error(e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send('```py\n{}{}\n```'.format(value, traceback.format_exc()))
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send('```py\n%s\n```' % value)
            else:
                self._last_result = ret
                await ctx.send('```py\n%s%s\n```' % (value, ret))


def setup(bot):
    bot.add_cog(Debug(bot))
