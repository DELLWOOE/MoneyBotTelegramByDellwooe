import requests

# токен бота
TOKEN = '6774099539:AAF6lMvwNFbPf_c8Hp9K2GfIdAMMFc7qW4Y'

# базовый URL API Telegram
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# функция для отправки сообщений в чат
def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    # формирование запроса
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    # отправка запроса
    response = requests.post(url, json=payload)
    return response.json()

# функция для начала работы бота
def start(update):
    chat_id = update["message"]["chat"]["id"]
    # отправка приветственного сообщения
    send_message(chat_id,
                 "Привет! Я бот для конвертации валют. Просто отправь мне сообщение с суммой и валютами для конвертации, например: '100 RUB USD'")

# функция для конвертации валюты
def convert(update):
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"].split(' ')

    if len(text) != 3:
        # проверка на правильный формат ввода
        send_message(chat_id, "Используйте формат: 100 RUB USD")
        return

    amount = text[0]
    from_currency = text[1].upper()
    to_currency = text[2].upper()

    # получение данных о курсах валют
    conversion_url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(conversion_url)
    data = response.json()

    if 'rates' not in data or to_currency not in data['rates']:
        # проверка на наличие информации о валютах
        send_message(chat_id, "Не удалось найти такую валюту.")
        return

    rate = data['rates'][to_currency]
    result = float(amount) * rate
    send_message(chat_id, f"{amount} {from_currency} = {result} {to_currency}")

# функция для обработки обновлений от Telegram API
def handle_updates(updates):
    for update in updates['result']:
        if 'message' in update and 'text' in update['message']:
            text = update['message']['text']
            chat_id = update['message']['chat']['id']
            if text.startswith('/start'):
                start(update)
            else:
                convert(update)

# получение обновлений от Telegram API
def get_updates(offset=None):
    url = BASE_URL + "getUpdates"
    params = {"timeout": 100, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

# основная функция для запуска бота
def main():
    update_id = None
    while True:
        updates = get_updates(offset=update_id)
        if len(updates['result']) > 0:
            update_id = updates['result'][-1]['update_id'] + 1
            handle_updates(updates)

# запуск основной функции
if __name__ == '__main__':
    main()

