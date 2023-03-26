import logging
import sys
import os

import requests
import telegram

import time

from dotenv import load_dotenv

from http import HTTPStatus


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Для всех "IF-исключений" можно создать отдельный файл исключений


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN))


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logger.debug('Начало отправки сообщения.')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Сообщение успешно отправлено! {}'.format(message))
    except Exception as error:
        logger.error('Сообщение не отправлено: {}'.format(error))


def get_api_answer(timestamp):
    """Функция делает запрос к эндпоинту API."""
    try:
        logger.debug(f'Начало запроса к API {ENDPOINT}.')
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_data': timestamp}
        )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise logger.error(
                'Проблема с доступом к странице: {}'.format(
                    homework_statuses.status_code
                )
            )
        logger.debug('Ответ получен: {}'.format(homework_statuses))
    except requests.exceptions.HTTPError as error:
        raise logger.error('Недоступность эндпоинта: {}'.format(error))
    except requests.RequestException as error:
        raise logger.error('Недоступность ответ: {}'.format(error))
    except Exception as error:
        raise logger.error('Был полочен неожиданный ответ: {}'.format(error))
    return homework_statuses.json()


def check_response(response: dict):
    """Проверяет ответ API на соответствие ключей."""
    logger.debug('Начало проверки ответа сервера.')
    if not isinstance(response, dict):
        raise logger.error('Некорректный тип ответа: {}'.format(TypeError))
    if not isinstance(response.get('homeworks'), list):
        raise logger.error('Некорректный тип ответа: {}'.format(TypeError))
    missed_keys = {'homeworks', 'current_date'} - response.keys()
    if missed_keys:
        raise logger.error(f'В ответе API нет ожидаемых ключей: {missed_keys}')
    return response['homeworks']


def parse_status(homework):
    """Извлекает статус домашней работы."""
    homework_name = homework.get('homework_name')
    missed_keys_name = {'homework_name'} - homework.keys()
    if missed_keys_name:
        raise logging.warning('Отсутствует имя домашней работы.')
    logger.debug(f'Проверяем: {homework_name}')
    homework_status = homework.get('status')
    missed_keys_status = {'status'} - homework.keys()
    if missed_keys_status:
        raise logger.error(f'Отсутствует ключ: {homework_status}')
    logger.debug(f'Текущий статус: {homework_status}')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if homework_status not in HOMEWORK_VERDICTS:
        raise logging.error(
            'Недокументированный статус домашней работы:',
            homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    last_send = {
        'error': None,
    }
    if not check_tokens():
        logger.critical('Отсутствует обязательная переменная окружения')
        sys.exit('Отсутствует обязательная переменная окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if len(homeworks) == 0:
                logging.debug('Ответ API пуст: нет домашних работ.')
            for homework in homeworks:
                message = parse_status(homework)
                if last_send.get(homework['homework_name']) != message:
                    send_message(bot, message)
                    last_send[homework['homework_name']] = message
            timestamp = response.get('current_date')
        except Exception as error:
            message = f'Сбой в программе: {error}'
            if last_send['error'] != message:
                send_message(bot, message)
                last_send['error'] = message
        else:
            last_send['error'] = None
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        stream=sys.stdout
    )
    main()
