import telebot
import pyowm
import config
from telebot import types
from pyowm.utils import timestamps
from pyowm.utils.config import get_default_config

config_dict = get_default_config()
config_dict['language'] = 'ru' 

owm = pyowm.OWM(config.owm_token, config_dict)
bot = telebot.TeleBot(config.bot_token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    sticker = open('res/sticker.webp', 'rb')
    
    bot.send_sticker(message.chat.id, sticker)
    bot.reply_to(message, 'Приветствую! Я погодный бот. Напиши мне любой город')

@bot.message_handler(content_types=['text'])
def send_echo(message):
    try:
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(message.text)
        forecaster = mgr.forecast_at_place(message.text, '3h')
        
        w = observation.weather
        temp = w.temperature('celsius')['temp']
        feel = w.temperature('celsius')['feels_like']
        wind = w.wnd['speed']
        
        answer = 'В городе ' + message.text + ': ' + w.detailed_status + '\n'
        answer += 'Температура: ' + str(temp) + ' C' + '\n'
        answer += 'Скорость ветра: ' + str(wind) + ' м/с' + '\n'
        answer += 'Влажность: ' + str(w.humidity) + '%' + '\n'
        answer += 'Ощущается как: ' + str(feel) + ' C' + '\n'
        
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='Прогноз на завтра', callback_data=message.text)
        keyboard.add(button)
        
        bot.send_message(message.chat.id, answer, reply_markup=keyboard)
    except Exception as error:
        log = 'Ошибка. А дело вот в чём:' + '\n' + str(error)
        bot.send_message(message.chat.id, log)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        try:
            mgr = owm.weather_manager()
            forecaster = mgr.forecast_at_place(call.data, '3h')
            
            tomorrow_at_9 = timestamps.tomorrow(9, 0)
            tomorrow_at_15 = timestamps.tomorrow(15, 0)
            tomorrow_at_21 = timestamps.tomorrow(21, 0)

            weather_at_9 = forecaster.get_weather_at(tomorrow_at_9)
            weather_at_15 = forecaster.get_weather_at(tomorrow_at_15)
            weather_at_21 = forecaster.get_weather_at(tomorrow_at_21)
     
            answer = 'Завтра утром: ' + weather_at_9.detailed_status + '\n'
            answer += 'Температура: ' + str(weather_at_9.temperature('celsius')['temp']) + ' C' + '\n'
            answer += 'Ветер: ' + str(weather_at_9.wnd['speed']) + ' м/с' + '\n'

            answer += '\n' + 'Завтра днём: ' + weather_at_15.detailed_status + '\n'
            answer += 'Температура: ' + str(weather_at_15.temperature('celsius')['temp']) + ' C' + '\n'
            answer += 'Ветер: ' + str(weather_at_15.wnd['speed']) + ' м/с' + '\n'

            answer += '\n' + 'Завтра вечером: ' + weather_at_21.detailed_status + '\n'
            answer += 'Температура: ' + str(weather_at_21.temperature('celsius')['temp']) + ' C' + '\n'
            answer += 'Ветер: ' + str(weather_at_21.wnd['speed']) + ' м/с' + '\n'
            
            bot.send_message(call.message.chat.id, answer)
        except Exception as error:
            log = 'Ошибка. А дело вот в чём:' + '\n' + str(error)
            bot.send_message(message.chat.id, log)

bot.polling()
