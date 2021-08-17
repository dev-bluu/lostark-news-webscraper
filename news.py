from lxml.html import fromstring
from aiohttp import ClientSession
from sqlite3 import Error
import hashlib
import sqlite3

BASE_URL = 'https://www.playlostark.com'


def _create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute('CREATE TABLE IF NOT EXISTS news_hashes(hash TEXT NOT NULL);')
        conn.commit()
    except Error as e:
        print(e)
    return conn


class NewsScraper:
    def __init__(self, loop=None, client=None, database=None):
        if loop is None and client is None:
            raise Exception()

        self.client = client if None else ClientSession(loop=loop)
        self.database = _create_connection('database/news.db') if database is None else database
        self._md5 = hashlib.new('md5', usedforsecurity=False)

    async def _fetch_url(self, url):
        async with self.client.get(url=url) as resp:
            return await resp.text()

    def _store_hash(self, _hash, table):
        with self.database as db:
            cur = db.cursor()
            cur.execute(f'INSERT INTO {table} VALUES(?);', (_hash,))
            db.commit()

    def _check_hash(self, _hash, table):
        with self.database as db:
            cur = db.cursor()
            cur.execute(f'SELECT * FROM {table} WHERE hash=?;', (_hash,))
            result = cur.fetchone()
        return result

    async def news_articles(self):
        """
        XPath: //div[@class="ags-SlotModule ags-SlotModule--blog ags-SlotModule--threePerRow"]
        :return:
        """
        url = BASE_URL + '/en-us/news'

        raw_html = await self._fetch_url(url)
        doc = fromstring(raw_html)
        article_box = doc.xpath('//div[@class="ags-SlotModule ags-SlotModule--blog ags-SlotModule--threePerRow"]')

        articles = []
        for article in article_box:
            article_meta = {
                'title': str(article.xpath('.//span[@class="ags-SlotModule-contentContainer-heading '
                                           'ags-SlotModule-contentContainer-heading '
                                           'ags-SlotModule-contentContainer-heading--blog"]/text()')[0]).strip(),
                'preview_text': str(article.xpath('.//div[@class="ags-SlotModule-contentContainer-text '
                                                  'ags-SlotModule-contentContainer-text--blog '
                                                  'ags-SlotModule-contentContainer-text"]/text()')[0]).strip(),
                'article_link': BASE_URL + article.xpath('.//a[@class="ags-SlotModule-spacer"]/@href')[0].strip(),
                'image_preview': 'https:' + article.xpath('.//img[@class="ags-SlotModule-imageContainer-image"]/@src')
                [0],
                'tag': str(article.xpath('.//h4[@class="ags-SlotModule-aboveImageBlogTag"]/text()')[0]).strip(),
            }

            _hash = hashlib.md5(article_meta.__str__().encode('UTF-8'), usedforsecurity=False).hexdigest()
            if self._check_hash(_hash, 'news_hashes'):
                return
            else:
                self._store_hash(_hash, 'news_hashes')

            articles.append(article_meta)
        return articles.reverse()

    async def close(self):
        await self.client.close()
