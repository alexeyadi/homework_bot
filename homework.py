import os
from dotenv import load_dotenv
from telegram import Bot
import requests
import time
import logging
import sys
from logging import StreamHandler


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

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
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Удачная отправка сообщения в Telegram')
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения в Telegram {error}')


def get_api_answer(current_timestamp=1) -> dict:
    """Get answer from API Praktikum."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params).json()
    if response:
        logger.info('Получен доступ к API')
        return response
    else:
        logger.error('API Яндекса не доступно')


def check_response(response) -> list:
    """Check API answer."""
    if response.get('homeworks'):
        logger.info('Получен корректный ответ от API')
        return response.get('homeworks')
    else:
        logger.error('Некорректный API')
        return None


def parse_status(homework) -> str:
    """Take info from particular homeworks."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if not homework_name:
        raise KeyError(f'Проблема с ключем: {homework_name}')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return verdict


def check_tokens() -> bool:
    """Checking tokens for availability."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Main logic bot's work."""
    if not check_tokens():
        logger.critical('Получены не все токены')
        sys.exit('Проблема с константами!')
    bot = Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            response = get_api_answer()
            homeworks_list = check_response(response)
            last_homework = homeworks_list[0]
            status = parse_status(last_homework)
            send_message(bot, status)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
