import aiohttp
import discord
import json
import logging
import random

from discord.ext import commands
from enum import Enum
from random import choice
from .utils.checks import send

log = logging.getLogger('LOG')


class RPS(Enum):
    rock = "\N{MOYAI}"
    paper = "\N{PAGE FACING UP}"
    scissors = "\N{BLACK SCISSORS}"


class RPSParser:
    def __init__(self, argument):
        argument = argument.lower()
        if argument == "rock":
            self.choice = RPS.rock
        elif argument == "paper":
            self.choice = RPS.paper
        elif argument == "scissors":
            self.choice = RPS.scissors
        else:
            raise


class Misc:
    def __init__(self, bot):
        self.bot = bot
        self.ball = ["As I see it, yes", "It is certain", "It is decidedly so", "Most likely", "Outlook good",
                     "Signs point to yes", "Without a doubt", "Yes", "Yes – definitely", "You may rely on it", "Reply hazy, try again",
                     "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]

    # Sends a googleitfor.me link with the specified tags
    @commands.command()
    async def l2g(self, ctx, *, msg: str):
        lmgtfy = 'http://googleitfor.me/?q='
        words = msg.lower().strip().split(' ')
        for word in words:
            lmgtfy += word + '+'
        await send(ctx, content=lmgtfy[:-1])

    # Picks a random answer from a list of options
    @commands.command()
    async def choose(self, ctx, *, choices: str):
        choiceslist = choices.split("|")
        choice = random.choice(choiceslist)
        if len(choiceslist) < 2:
            await send(ctx, content="2+ Options, separated with ``|``",  ttl=5)
        else:
            message = "<:robot:273922151856209923> | My Answer is ``{0}``"
            await send(ctx, content=message.format(choice), delete=False)
        await ctx.message.edit(content='Options:| %s |' % choices)

    # 8ball
    @commands.command(name="8", aliases=["8ball"])
    async def _8ball(self, ctx, *, question: str):
        if question.endswith("?") and question != "?":
            await send(ctx, content="`" + choice(self.ball) + "`", delete=False)
        else:
            await send(ctx, content="That doesn't look like a question.", ttl=3)

    # RPS
    @commands.command()
    async def rps(self, ctx, your_choice: RPSParser):
        player_choice = your_choice.choice
        bot_choice = choice((RPS.rock, RPS.paper, RPS.scissors))
        cond = {
                (RPS.rock,     RPS.paper): False,
                (RPS.rock,     RPS.scissors): True,
                (RPS.paper,    RPS.rock): True,
                (RPS.paper,    RPS.scissors): False,
                (RPS.scissors, RPS.rock): False,
                (RPS.scissors, RPS.paper): True
               }
        if bot_choice == player_choice:
            outcome = None
        else:
            outcome = cond[(player_choice, bot_choice)]

        if outcome is True:
            await send(ctx, content="{} You win!".format(bot_choice.value), delete=False)
        elif outcome is False:
            await send(ctx, content="{} You lose!".format(bot_choice.value), delete=False)
        else:
            await send(ctx, content="{} We're square!".format(bot_choice.value), delete=False)

    # Urbandictionary
    @commands.command()
    async def urban(self, ctx, *, search_terms: str, definition_number: int=1):
        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11):
                pos = 0
        except ValueError:
            pos = 0
        search_terms = "+".join(search_terms)
        url = "http://api.urbandictionary.com/v0/define?term=" + search_terms
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as r:
                    result = json.loads(await r.text())
                    if result["list"]:
                        definition = result['list'][pos]['definition']
                        example = result['list'][pos]['example']
                        defs = len(result['list'])
                        embed = discord.Embed(title='Definition #{} out of {}'.format(pos+1, defs), description=definition, colour=0x9b59b6)
                        embed.set_author(name=search_terms, icon_url='https://i.imgur.com/bLf4CYz.png')
                        embed.add_field(name="Example:", value=example, inline=False)
                        await send(ctx, embed=embed)
                    else:
                        await send(ctx, content="Your search terms gave no results.", ttl=3)
        except IndexError:
            await send(ctx, content="There is no definition #{}".format(pos+1), ttl=3)
        except:
            await send(ctx, content="Error.", ttl=3)

    @commands.command()
    async def gif(self, ctx, *text):
        if text:
            if len(text[0]) > 1 and len(text[0]) < 20:
                try:
                    msg = "+".join(text)
                    search = "http://api.giphy.com/v1/gifs/search?q=" + msg + "&api_key=dc6zaTOxFJmzC"
                    async with aiohttp.ClientSession() as cs:
                        async with cs.get(search) as r:
                            result = json.loads(await r.text())
                            if result["data"] != []:
                                url = result["data"][0]["images"]["original"]["url"]
                                await send(ctx, content=url)
                            else:
                                await send(ctx, content="Your search terms gave no results.", ttl=3)
                except:
                    await send(ctx, content="Error.", ttl=3)
            else:
                await send(ctx, content="Invalid search.", ttl=3)
        else:
            await send(ctx, content="\N{HEAVY EXCLAMATION MARK SYMBOL} Specify Search", ttl=3)


def setup(bot):
    bot.add_cog(Misc(bot))
