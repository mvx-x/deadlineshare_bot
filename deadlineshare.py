import telebot
import random
from datetime import datetime

# Инициализация бота
API_TOKEN = '7599299931:AAHShSxV-4mt2Mkxov9KSI6qEteQjdoZJKI'
bot = telebot.TeleBot(API_TOKEN)

# Общая память для хранения дедлайнов
deadlines = {}

# Списки дедлайнов для каждого пользователя
user_deadlines = {}

def generate_unique_id():
    """
    Генерирует уникальный 6-значный числовой ID.

    Returns:
        str: Уникальный 6-значный числовой ID.
    """
    while True:
        unique_id = str(random.randint(100000, 999999))
        if unique_id not in deadlines:
            return unique_id

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Отправляет приветственное сообщение пользователю.

    Args:
        message (telebot.types.Message): Объект сообщения от пользователя.

    Returns:
        None
    """
    bot.reply_to(message, "Добро пожаловать в DeadlineShare Bot!")

@bot.message_handler(commands=['add'])
def add_deadline(message):
    """
    Добавляет дедлайн с датой, описанием и уникальным ID.

    Args:
        message (telebot.types.Message): Объект сообщения от пользователя.

    Returns:
        None
    """
    try:
        _, date, description = message.text.split(' ', 2)
        unique_id = generate_unique_id()
        deadlines[unique_id] = (date, description)

        # Добавляет дедлайн в список создателя
        user_id = message.from_user.id
        if user_id not in user_deadlines:
            user_deadlines[user_id] = {}
        user_deadlines[user_id][unique_id] = (date, description)

        bot.reply_to(message, f"Дедлайн '{description}' на {date} добавлен с ID [{unique_id}]")
    except ValueError:
        bot.reply_to(message, "Использование: /add ГГГГ-ММ-ДД описание")

@bot.message_handler(commands=['list'])
def list_deadlines(message):
    """
    Выводит список всех дедлайнов для конкретного пользователя.

    Args:
        message (telebot.types.Message): Объект сообщения от пользователя.

    Returns:
        None
    """
    user_id = message.from_user.id
    if user_id not in user_deadlines or not user_deadlines[user_id]:
        bot.reply_to(message, "Дедлайны не найдены.")
        return

    sorted_deadlines = sorted(user_deadlines[user_id].items(), key=lambda x: datetime.strptime(x[1][0], '%Y-%m-%d'))
    response = "Дедлайны:\n"
    for i, (unique_id, (date, description)) in enumerate(sorted_deadlines, start=1):
        response += f"{i}. {date} - {description} [{unique_id}]\n"

    bot.reply_to(message, response)

@bot.message_handler(commands=['del'])
def delete_deadline(message):
    """
    Удаляет дедлайн по его номеру в списке.

    Args:
        message (telebot.types.Message): Объект сообщения от пользователя.

    Returns:
        None
    """
    try:
        _, number = message.text.split(' ', 1)
        number = int(number)
        user_id = message.from_user.id

        if user_id not in user_deadlines or number <= 0 or number > len(user_deadlines[user_id]):
            bot.reply_to(message, "Неверный номер дедлайна.")
            return

        sorted_deadlines = sorted(user_deadlines[user_id].items(), key=lambda x: datetime.strptime(x[1][0], '%Y-%m-%d'))
        unique_id = list(sorted_deadlines)[number - 1][0]
        del user_deadlines[user_id][unique_id]

        # Проверяет, существует ли дедлайн в списке любого пользователя
        if not any(unique_id in user_list for user_list in user_deadlines.values()):
            del deadlines[unique_id]

        bot.reply_to(message, f"Дедлайн номер {number} удален из вашего списка.")
    except ValueError:
        bot.reply_to(message, "Использование: /del номер")

@bot.message_handler(commands=['add_id'])
def add_deadline_by_id(message):
    """
    Добавляет дедлайн по его уникальному ID.

    Args:
        message (telebot.types.Message): Объект сообщения от пользователя.

    Returns:
        None
    """
    try:
        _, unique_id = message.text.split(' ', 1)
        unique_id = unique_id.strip('[]')
        user_id = message.from_user.id

        if unique_id in deadlines:
            date, description = deadlines[unique_id]
            if user_id not in user_deadlines:
                user_deadlines[user_id] = {}
            user_deadlines[user_id][unique_id] = (date, description)
            bot.reply_to(message, f"Дедлайн '{description}' на {date} добавлен с ID [{unique_id}]")
        else:
            bot.reply_to(message, f"Дедлайн с ID [{unique_id}] не найден.")
    except ValueError:
        bot.reply_to(message, "Использование: /add_id [unique_id]")

@bot.message_handler(commands=['edit'])
def edit_deadline(message):
    """
    Изменяет дату и описание существующего дедлайна по его уникальному ID.

    Args:
        message (telebot.types.Message): Объект сообщения от пользователя.

    Returns:
        None
    """
    try:
        _, unique_id, new_date, new_description = message.text.split(' ', 3)
        unique_id = unique_id.strip('[]')
        user_id = message.from_user.id

        if unique_id in user_deadlines.get(user_id, {}):
            deadlines[unique_id] = (new_date, new_description)
            user_deadlines[user_id][unique_id] = (new_date, new_description)
            bot.reply_to(message, f"Дедлайн с ID [{unique_id}] обновлен до '{new_description}' на {new_date}.")
        else:
            bot.reply_to(message, f"Дедлайн с ID [{unique_id}] не найден в вашем списке.")
    except ValueError:
        bot.reply_to(message, "Использование: /edit [unique_id] ГГГГ-ММ-ДД новое_описание")

# Обновлять в ожидании изменений
print("Бот запущен...")
bot.polling()