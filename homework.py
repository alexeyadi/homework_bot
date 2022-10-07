import os
from dotenv import load_dotenv
from telegram import Bot
import requests
import time
import logging
import exceptions
import sys
from http import HTTPStatus
from logging import StreamHandler


load_dotenv()
logger = logging.getLogger(__name__)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message) -> str:
    """Send message from bot to student."""
    logger.debug('Приступаем к отправке сообщения в Telegram...')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        raise exceptions.Response(
            f'Сбой при отправке сообщения в Telegram {error}'
        )
    else:
        logger.info('Удачная отправка сообщения в Telegram')


def get_api_answer(current_timestamp=1) -> dict:
    """Get answer from API Praktikum."""
    logger.debug('Начинаем проверку ответа от API...')
    timestamp = current_timestamp or int(time.time())
    request_params = {'params': {'from_date': timestamp}, 'headers': HEADERS,
                      'url': ENDPOINT}
    try:
        response = requests.get(**request_params)
    except Exception as error:
        logger.error(f'Ошибка получения API: {error}')
    if response.status_code != HTTPStatus.OK:
        message = ('Ошибка: статус страницы'
                   f'{response.status_code}, {ENDPOINT}, {HEADERS}'
                   )
        raise exceptions.Response(message)
    try:
        return response.json()
    except Exception:
        logger.error('Невалидный json')


def check_response(response) -> list:
    """Check API answer."""
    if not isinstance(response, dict):
        message = (f'Неверный тип данных: {dict}')
        raise TypeError(message)
    homework = response.get('homeworks')
    if homework is None:
        raise exceptions.Response('Данных нет')
    elif not isinstance(homework, list):
        message = (f'Неверный тип данных: {list}')
        raise TypeError(message)
    elif homework:
        logger.info('Получен корректный ответ от API')
        return homework
    else:
        logger.error('Некорректный API')
        return None


def parse_status(homework) -> str:
    """Take info from particular homeworks."""
    if not homework:
        logger.error('Не передана домашняя работа')
        raise ValueError('Нет домашней работы')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if not homework_name:
        raise KeyError(f'Проблема с ключем: {homework_name}')
    if homework_status not in HOMEWORK_VERDICTS:
        message = (
            f'Отсутствует ключ {homework_status}')
        logger.error(message)
        raise KeyError(message)
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Checking tokens for availability."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Main logic bot's work."""
    if not check_tokens():
        logger.critical('Получены не все токены')
        sys.exit('Проблема с константами!')
    bot = Bot(token=TELEGRAM_TOKEN)
    last_status_value = dict()
    while True:
        try:
            response = get_api_answer()
            homeworks_list = check_response(response)
            last_homework = homeworks_list[0]
            status = parse_status(last_homework)
            last_status_value[last_homework.get('homework_name')] = status
            if last_status_value[last_homework.get('homework_name')] != status:
                send_message(bot, status)
            else:
                logger.debug('Статус проверки не изменился')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        'Строка %(lineno)d - %(funcName)s - %(asctime)s - %(name)s'
        ' - %(levelname)s - %(message)s'
    )
    handler = StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    main()
