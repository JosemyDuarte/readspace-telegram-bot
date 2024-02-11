import asyncio
import random

import telegram

from omnivore import OmnivoreQLClient, ArticleDownloader


class HighlightSender:
    def __init__(self, max_length: int = 4096, max_messages_per_second: int = 30, telegram_bot_token: str = None):
        self.max_length: int = max_length
        self.max_messages_per_second: int = max_messages_per_second
        self.bot = telegram.Bot(token=telegram_bot_token)

    async def send_highlights(self, chat_id: str, token: str, label: str, amount: int = 1) -> bool:
        omnivore_client = OmnivoreQLClient(token)
        article_downloader = ArticleDownloader(omnivore_client)
        downloaded_articles = article_downloader.download_articles(label)

        if len(downloaded_articles) == 0:
            return False

        if len(downloaded_articles) > amount:
            downloaded_articles = random.sample(downloaded_articles, amount)

        text = ''
        for article in downloaded_articles:
            text += f'<b>{article["node"]["title"]}</b>:\n'
            for highlight in article['node']['highlights']:
                text += highlight['quote'] + '\n\n'
            text += '\n'
            if len(text) > self.max_length:
                await self.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
                await asyncio.sleep(2)
                text = ''
        if len(text) > 0:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
            await asyncio.sleep(2)

        return True
