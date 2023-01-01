from collections import deque
from telethon import TelegramClient, events

from config import api_id, api_hash, gazp_show_source, telegram_channels


def telegram_parser(session, api_id, api_hash, telegram_channels, posted_q,
                    n_test_chars=50, check_pattern_func=None,
                    send_message_func=None, logger=None, loop=None):
    '''Телеграм парсер'''

    # Ссылки на телеграмм каналы
    telegram_channels_links = list(telegram_channels.values())

    client = TelegramClient(session, api_id, api_hash,
                            base_logger=logger, loop=loop)
    client.start()

    @client.on(events.NewMessage(chats=telegram_channels_links))
    async def handler(event):
        '''Забирает посты из телеграмм каналов и посылает их в наш канал'''
        if event.raw_text == '':
            return

        news_text = ' '.join(event.raw_text.split('\n')[:2])

        if not (check_pattern_func is None):
            if not check_pattern_func(news_text):
                return

        head = news_text[:n_test_chars].strip()

        if head in posted_q:
            return

        if gazp_show_source:
            source = telegram_channels[event.message.peer_id.channel_id]
            link = f'{source}/{event.message.id}'
            channel = '@' + source.split('/')[-1]
            post = f'<b>{channel}</b>\n{link}\n{news_text}'
        else:
            post = f'{news_text}'

        if send_message_func is None:
            print(post, '\n')
        else:
            await send_message_func(post)

        posted_q.appendleft(head)

    return client


if __name__ == "__main__":


    # Очередь из уже опубликованных постов, чтобы их не дублировать
    posted_q = deque(maxlen=20)

    client = telegram_parser('gazp', api_id, api_hash, telegram_channels, posted_q)

    client.run_until_disconnected()
