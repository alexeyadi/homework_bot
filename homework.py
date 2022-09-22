import os
from dotenv import load_dotenv
from telegram import Bot
import requests
import time
import logging
import sys
from logging import StreamHandler


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message) -> str:
    """Send message from bot to student."""
    bot.send_message(message)

def get_api_answer(current_timestamp=None) -> dict:
    """Get answer from API Praktikum."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params).json()
    if response:
        return response

def check_response(response) -> dict:
    """Answer API is correctly?"""
    return response.get('homeworks') if response.get("homeworks") else None

def parse_status(homework) -> str:
    """Take info from particular homeworks."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get('homework_status')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'

def check_tokens() -> bool:
    """Checking tokens for availability."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])

def main():
    """Main logic bot's work."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = get_api_answer()

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()



# def main():
#     """Main logic bot's work."""

#     ...

#     bot = telegram.Bot(token=TELEGRAM_TOKEN)
#     current_timestamp = int(time.time())

#     ...

#     while True:
#         try:
#             response = ...

#             ...

#             current_timestamp = ...
#             time.sleep(RETRY_TIME)

#         except Exception as error:
#             message = f'Сбой в работе программы: {error}'
#             ...
#             time.sleep(RETRY_TIME)
#         else:
#             ...


# if __name__ == '__main__':
#     main()