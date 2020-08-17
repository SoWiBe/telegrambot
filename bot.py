# всякие библиотеки
import requests  # для отправки https запроса на сайт колледжа
import lxml.html  # испльзую ее, потому что можно обращаться не по классу, а по индексу tr, td
from lxml import etree
from selenium import webdriver  # основной инструмент для парсинга
from bs4 import BeautifulSoup
import telebot
from telebot import types
from datetime import datetime, date, time, timedelta
import schedule
import time
import threading

# Translate code...
from googletrans import Translator


def translate_text(text):
    translator = Translator()
    r = translator.translate(text)
    return r.text
# End Translate code...


# токен
bot = telebot.TeleBot('1237386405:AAE5wVdNkMLVBtlpkOo5LzNo1TCTO6M0CNw')


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}


# код для асихронного выполнения
schedstop = threading.Event()


def timer():
    while not schedstop.is_set():
        schedule.run_pending()
        time.sleep(3)


schedthread = threading.Thread(target=timer)
schedthread.start()
# конец кода для асихронного выполнения


# итератор для 1, 2, 3 пары
# первой паре соответствует 5 строчка таблицы, второй паре 6 строчка и тд
lesson = [5, 6, 7]

# словарь для столбцов,
# каждому дню недели соответствует свой номер столбца
# таким образом если у нас вторник, то расписание извлекать из 4 столбца
day_of_week_1 = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8,
                 7: 9}

day_of_week_2 = {1: 10, 2: 11, 3: 12, 4: 13, 5: 14, 6: 15, 7: 16}

# словарь, для красивого вывода дня недели в итоговом сообщении
name_week = {1: "Понедельник", 2: "Вторник", 3: "Среда",
                4: "Четверг", 5: "Пятница", 6: "Суббота", 7: "Воскресенье"}

# если пользователь запросить расписание до того, как оно было сформировано
today_table = "Попробуйте позже..."
yesterday_table = "Попробуйте позже..."
tomorrow_table = "Попробуйте позже..."


def make_timetable(weekday, day):
    """
    Функция парсинга, в параметрах указываем день недели,
    и сам день (сегодня, вчера, завтра)
    """
    count_week = day.isocalendar()[1]
    lessons = []
    global result
    print("\nParsing " + name_week[weekday])
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.get(
        'https://www.oat.ru/sites/default/downloads/schedule/rspcls37.html')
    if count_week % 2 != 0:
        week = "1-"
        for i in range(3):
            # самое главное -
            # в список lessons я добавляю текст из определенной ячейки таблицы
            # адрес ячейки - итерируемый lesson (1, 2, 3) и день недели, которому соответствует свой номер столбца
            lessons.append(driver.find_element_by_xpath(
                f'/html/body/table/tbody/tr[{lesson[i]}]/td[{day_of_week_1[weekday]}]'))

    elif count_week % 2 == 0:
        week = "2-"
        for i in range(3):
            # самое главное -
            # в список lessons я добавляю текст из определенной ячейки таблицы
            # адрес ячейки - итерируемый lesson (1, 2, 3) и день недели, которому соответствует свой номер столбца
            lessons.append(driver.find_element_by_xpath(
                f'/html/body/table/tbody/tr[{lesson[i]}]/td[{day_of_week_2[weekday]}]'))

    result = "Расписание на " + \
        week + name_week[weekday] + "\n\n"

    for elem in lessons:
        result += elem.text + "\n\n"

    driver.quit()
    return result


def make_all():
    """
    Основная функция
    При ее вызове мы вычисляем все даты и дни недели
    Потом используем эти вычисления в качестве параметров для функции парсинга
    """
    print("\nСalculating the date...")
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    print("Successfully")

    print("\nСalculating the weekday...")
    today_weekday = today.isoweekday()
    yesterday_weekday = (today - timedelta(days=1)).isoweekday()
    tomorrow_weekday = (today + timedelta(days=1)).isoweekday()
    print("Successfully")

    print("\n\nStarting parsing...")
    global today_table
    today_table = make_timetable(today_weekday, today)
    print("Successfully")
    global yesterday_table
    yesterday_table = make_timetable(yesterday_weekday, yesterday)
    print("Successfully")
    global tomorrow_table
    tomorrow_table = make_timetable(tomorrow_weekday, tomorrow)
    print("Successfully")
    print("\nThe parsing process was successful")


@ bot.message_handler(commands=['start'])
def sendMsg(message):
    bot.send_message(message.chat.id, "Приветствую...")
    bot.send_message(message.chat.id, """
    Мои команды:
    /weather погода в Омске
    /help помощь
    /timetable показать расписание
    """)


@ bot.message_handler(commands=['weather'])
def getWeather(message):
    """
    Отправляет погоду постредством парсинга с GisMeteo
    """
    resp = requests.get(
        'https://www.gismeteo.ru/weather-omsk-4578/', headers=headers).text
    soup = BeautifulSoup(resp, 'html.parser')

    title = soup.find('span', class_=('tab-weather__value_l'))
    weather__count = title.get_text()
    bot.send_message(message.chat.id, weather__count)


@ bot.message_handler(commands=['timetable'])
def send_timetable(message):
    try:
        global keyboard
        keyboard = types.InlineKeyboardMarkup()

        today = types.InlineKeyboardButton(
            text="Today", callback_data="Today")
        keyboard.add(today)

        yesterday = types.InlineKeyboardButton(
            text="Yesterday", callback_data="Yesterday")
        keyboard.add(yesterday)

        tomorrow = types.InlineKeyboardButton(
            text="Tomorrow", callback_data="Tomorrow")
        keyboard.add(tomorrow)

        bot.send_message(message.from_user.id, text="---------------------------------------------",
                         reply_markup=keyboard)

    except Exception as error:
        print("Ошибка...", error)


@ bot.message_handler(commands=['help'])
def sendCmd(message):
    bot.send_message(message.chat.id, """
    Мои команды:
    /weather
    /timetable
    /help
    """)


@ bot.message_handler(commands=['news'])
def send_news(message):
    # resp = requests.get(
    #     'https://www.gismeteo.ru/weather-omsk-4578/', headers=headers).text
    # soup = BeautifulSoup(resp, 'html.parser')

    # title = soup.find('span', class_=('tab-weather__value_l'))
    # weather__count = title.get_text()
    # bot.send_message(message.chat.id, weather__count)
    pass


@bot.message_handler(content_types="text")
def translate(message):
    # perevod = translate_text(message.text)
    bot.send_message(message.chat.id, translate_text(message.text))


# обработчик событий
# обрабатывает нажатия по кнопкам

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global keyboard, today_table, yesterday_table, tomorrow_table
    if call.data == 'Today':
        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text=today_table, reply_markup=keyboard)

        except Exception as error:
            print("Ошибка вызова Today: ", error)

    if call.data == 'Yesterday':
        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text=yesterday_table, reply_markup=keyboard)

        except Exception as error:
            print("Ошибка вызова Yesterday: ", error)

    if call.data == 'Tomorrow':
        try:

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text=tomorrow_table, reply_markup=keyboard)

        except Exception as error:
            print("Ошибка вызова Tomorrow: ", error)


try:
    schedule.every(60).seconds.do(make_all)
except Exception:
    print("Ошибка")
# schedule.every().day.at("18:10").do(make_all)


bot.polling(none_stop=True)
