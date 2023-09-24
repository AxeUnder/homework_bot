# homework_bot
Это telegram bot, который проверяет статус домашней работы через API-сервис Yandex.Practicum, если статус сданных проектов изменится, то бот оповестит об этом.

**Инструменты и стек:** #Python #Requests #Python-telegram-bot #Http #Python-dotenv #Pytest #Telegram

## Запуск проекта
1. Форкаем проект и клонируем его на сервер.
   ```bash
   git clone git@github.com:<ваш репозиторий>/homework_bot.git
   ```
2. Подготовим .env файл.
   ```bash
   nano .env
   ```
   ```nano
   PRACTICUM_TOKEN=<ваш yandex-ID>
   TELEGRAM_TOKEN=<ваш токен тг>
   TELEGRAM_CHAT_ID=<токен вашего тг бота>
   ```
3. Запускаем бота на сервере.
   ```bash
   python3 homework.py
   ```

## Об авторе
Python-разработчик
>[AxeUnder](https://github.com/AxeUnder).
