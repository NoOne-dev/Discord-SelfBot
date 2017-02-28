import aiohttp
import discord
import logging
import spice_api as spice

from bs4 import BeautifulSoup
from discord.ext import commands
from lxml import etree
from urllib.parse import parse_qs
from .utils import config
from .utils.checks import perms

log = logging.getLogger('LOG')


class Mal:

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('config.json')

    async def get_google_entries(self, query, search):
        params = {
            'as_q': search,
            'as_epq': query,
            'as_sitesearch': 'myanimelist.net'
            }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'
            }
        entries = []
        async with aiohttp.get('https://www.google.com/search', params=params, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError('Google somehow failed to respond.')
            root = etree.fromstring(await resp.text(), etree.HTMLParser())
            search_nodes = root.findall(".//div[@class='g']")
            for node in search_nodes:
                url_node = node.find('.//h3/a')
                if url_node is None:
                    continue
                url = url_node.attrib['href']
                if not url.startswith('/url?'):
                    continue
                if search in url:
                    if ('/recommendations/' in url) or ('/character/' in url) or ('/featured/' in url):
                        continue
                    url = parse_qs(url[5:])['q'][0]
                    entries.append(url)
            try:
                if entries is not None:
                    content = entries[0].split('/')[4]
                    link = entries[0]
                else:
                    content, link = None
            except:
                return None, None
            return content, link

    async def parse_content(self, i, link, _type):
        mal = spice.search_id(int(i), spice.get_medium(_type), spice.init_auth(self.config.get('mal_username', {}), self.config.get('mal_password', {})))
        synopsis = BeautifulSoup(mal.synopsis, 'lxml').get_text().replace('[i]', '').replace('[/i]', '')
        synnew = ''
        for i in synopsis.split('.'):
            if (len(synnew + i + '.')) <= 1024:
                    synnew += i + '.'
            else:
                synnew += '..'
        if (mal.raw_data.start_date is None) or ('00' in mal.raw_data.start_date.text):
            start = 'Unknown'
        else:
            start = mal.raw_data.start_date.text
        if (mal.raw_data.end_date is None) or ('00' in mal.raw_data.end_date.text):
            end = 'Unknown'
        else:
            end = mal.raw_data.end_date.text
        e = discord.Embed(colour=0x0057e7, description='**Alternative:** {}'.format(mal.english), url=link)
        e.set_author(name=mal.title, icon_url='https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png')
        e.set_thumbnail(url=mal.image_url)
        e.add_field(name='Synopsis', value=synnew.replace('[Written by MAL Rewrite].', ''), inline=False)
        e.add_field(name='Score', value=mal.score + '/10', inline=True)
        if _type is 'anime':
            e.add_field(name='Episodes', value=mal.episodes, inline=True)
            e.add_field(name='Type', value=mal.anime_type, inline=True)
        elif _type is 'manga':
            chap = 'Unknown' if mal.chapters == '0' else mal.chapters
            e.add_field(name='Chapters', value=chap, inline=True)
            e.add_field(name='Type', value=mal.manga_type, inline=True)
        e.add_field(name='Status', value=mal.status, inline=True)
        if _type is 'anime':
            e.set_footer(text='Aired: {} - {}'.format(start, end))
        elif _type is 'manga':
            e.set_footer(text='Published: {} - {}'.format(start, end))
        return e

    # MyAnimelist Anime
    @commands.command()
    async def anime(self, ctx, *, query):
        await ctx.message.delete()
        se = await ctx.send(content='Searching...')
        try:
            i, link = await self.get_google_entries(query, 'anime')
        except RuntimeError as e:
            await ctx.send(str(e), delete_after=3)
        else:
            if (i is None) or (not i.isdigit()):
                await se.delete()
                return await ctx.send('No results found... sorry.', delete_after=3)
            else:
                em = await self.parse_content(i, link, 'anime')
                try:
                    if perms(ctx.message):
                        await ctx.send(embed=em)
                    else:
                        await ctx.send(link)
                except:
                    await ctx.send('Error!, Embed might have failed you', delete_after=3)
                await se.delete()

    # MyAnimelist Manga
    @commands.command()
    async def manga(self, ctx, *, query):
        await ctx.message.delete()
        se = await ctx.send(content='Searching...')
        try:
            i, link = await self.get_google_entries(query, 'manga')
        except RuntimeError as e:
            await ctx.send(str(e), delete_after=3)
        else:
            if (i is None) or (not i.isdigit()):
                await se.delete()
                return await ctx.send('No results found... sorry.', delete_after=3)
            else:
                em = await self.parse_content(i, link, 'manga')
                try:
                    if perms(ctx.message):
                        await ctx.send(embed=em)
                    else:
                        await ctx.send(link)
                except:
                    await ctx.send('Error!, Embed might have failed you', delete_after=3)
                await se.delete()


def setup(bot):
    bot.add_cog(Mal(bot))
