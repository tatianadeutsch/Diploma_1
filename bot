from keyboard import sender
from main import *


for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        msg = event.text.lower()
        sender(user_id, msg.lower())
        if request == 'новый поиск':
            creating_database()
            bot.write_msg(user_id, f'Привет, {bot.name(user_id)}')
            bot.find_user(user_id)
            bot.write_msg(event.user_id, f'Ваш визави найден! Выберите "Результат"')
            bot.find_persons(user_id, offset)

        elif request == 'результат':
            for i in line:
                offset += 1
                bot.find_persons(user_id, offset)
                if request == 'в избранное':
                    bot.user_favorites(user_id, offset)
                break

        else:
            bot.write_msg(event.user_id, 'Ваше сообщение непонятно')
