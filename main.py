from datetime import datetime as dt
from dotenv import load_dotenv
from news import NewsScraper
from os.path import join, dirname
import schedule
import os
import asyncio
import json
import time
import logging
import ast

logging.basicConfig(filename="lanews.log", level=logging.DEBUG)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PRELOAD = ast.literal_eval(os.environ.get('PRELOAD'))
if WEBHOOK_URL is None:
    raise Exception()
if PRELOAD is None:
    PRELOAD = True

loop = asyncio.get_event_loop()


async def preload_news():
    scraper = NewsScraper(loop=loop)
    await fetch_news(scraper)
    await scraper.close()


async def fetch_news(scraper):
    logging.debug('Running web scrape...')
    return await scraper.news_articles()


async def publish_news():
    la_news = NewsScraper(loop=loop)
    articles = await fetch_news(la_news)

    if bool(articles):
        for article in articles:
            payload = {
                "content": '<@&922576289188151307>',
                "embeds": [
                    {
                        "title": article['title'].replace("'", "\\'"),
                        "description": article['preview_text'].replace("'", "\\'"),
                        "url": article['article_link'].replace("'", "\\'"),
                        "color": 5814783,
                        "footer": {
                            "text": article['tag']
                        },
                        "timestamp": f"{dt.utcnow()}",
                        "image": {
                            "url": article['image_preview']
                        },
                        "thumbnail": {
                            "url": "https://images.ctfassets.net/umhrp0op95v1/S3yKwaVAOi8Bgqg4n4scf"
                                   "/adae769671b271b88f97d31721432986/LA_LOGO.png "
                        }
                    }
                ]
            }
            while True:
                resp = await la_news.client.post(url=WEBHOOK_URL, data=json.dumps(payload).encode('UTF-8'), headers={'Content-Type': 'application/json'})
                if resp.status == 204:
                    break
                time.sleep(15)
        time.sleep(5)
    await la_news.close()


def run_async(coroutine):
    task = coroutine()
    loop.run_until_complete(task)


if PRELOAD:
    asyncio.get_event_loop().run_until_complete(preload_news())

schedule.every(1).seconds.do(run_async, publish_news)

while True:
    logging.debug('Checking schedule...')
    schedule.run_pending()
    time.sleep(1)
