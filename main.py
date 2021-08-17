from datetime import datetime as dt
from dotenv import load_dotenv
from news import NewsScraper
from os.path import join, dirname
import schedule
import os
import asyncio
import json
import time

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
loop = asyncio.get_event_loop()


async def publish_news():
    print('Running web scrape...')
    la_news = NewsScraper(loop=loop)
    articles = await la_news.news_articles()

    if bool(articles):
        for article in articles:
            payload = {
                "content": None,
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
                        #"thumbnail": {
                        #    "url": "https://images.ctfassets.net/umhrp0op95v1/S3yKwaVAOi8Bgqg4n4scf"
                        #           "/adae769671b271b88f97d31721432986/LA_LOGO.png "
                        #}
                    }
                ]
            }
            resp = await la_news.client.post(url=WEBHOOK_URL, data=json.dumps(payload).encode('UTF-8'), headers={'Content-Type': 'application/json'})
            print(resp.status)
    await la_news.close()


def run_async(coroutine):
    task = coroutine()
    loop.run_until_complete(task)


schedule.every().hour.do(run_async, publish_news)

while True:
    print('Checking schedule...')
    schedule.run_pending()
    time.sleep(300)
