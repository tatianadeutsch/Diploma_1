from config import TOKEN_GROUP, TOKEN_APP, offset, line
import vk_api
import requests
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from database import *


class VKBot:
    def __init__(self):
        print('Ура! Бот наконец-то создан!')
        self.vk = vk_api.VkApi(token=TOKEN_APP)
        self.longpoll = VkLongPoll(self.vk)
        self.url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': TOKEN_GROUP,
            'v': '5.131'
        }

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    # Определить имя пользователя, написавшему боту
    def name(self, user_id):
        url_name = self.url + 'users.get'
        params = {'user_ids': user_id,
                  }
        response = requests.get(url_name, params={**self.params, **params}).json()

        information_dict = response['response']
        for i in information_dict:
            for key, value in i.items():
                first_name = i.get('first_name')
                return first_name

    # Запросить возраст визави пользователя: ОТ
    def get_age_low(self, user_id):
        url_age_low = self.url + 'users.get'
        params = {'user_ids': user_id,
                  'fields': 'bdate'}
        response = requests.get(url_age_low, params={**self.params, **params}).json()

        information_list = response['response']
        self.write_msg(user_id, 'Введите возраст для своего визави (от 18 лет): ')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                age = event.text
                return age

    # Запросить возраст визави пользователя: ДО
    def get_age_high(self, user_id):
        url_age_high = self.url + 'users.get'
        params = {'user_ids': user_id,
                  'fields': 'bdate'}
        response = requests.get(url_age_high, params={**self.params, **params}).json()

        self.write_msg(user_id, 'Введите возраст для своего визави (до 99 лет) ')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                age = event.text
                return age

    # Запросить пол визави пользователя
    def get_sex(self, user_id):
        url_get_sex = self.url + 'users.get'
        params = {'user_ids': user_id,
                  'fields': 'sex'}
        response = requests.get(url_get_sex, params={**self.params, **params}).json()

        self.write_msg(user_id, 'Пол вашей пары:\n'
                                '1 - женщина\n'
                                '2 - мужчина\n'
                                '0 - любой')

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                sex = event.text
                return sex

    # Адаптация названия города к ИД города
    def cities(self, user_id, city_name):
        url_cities = self.url + 'database.getCities'
        params = {'country_id': 1,
                  'q': f'{city_name}',
                  'need_all': 0,
                  'count': 1000,
                  'v': '5.131'}
        response = requests.get(url_cities, params={**self.params, **params}).json()
        try:
            information_list = response['response']
            list_cities = information_list['items']
            for i in list_cities:
                found_city_name = i.get('title')
                if found_city_name == city_name:
                    found_city_id = i.get('id')
                    return int(found_city_id)
        except KeyError:
            self.write_msg(user_id, 'Ошибка')

    # Запросить название города визави пользователя
    def find_city(self, user_id):
        url_city = self.url + 'users.get'
        params = {'fields': 'city',
                  'user_ids': user_id,
                  'country_id': 1,
                  'need_all': 0,
                  'count': 1000,
                  }
        response = requests.get(url_city, params={**self.params, **params}).json()

        self.write_msg(user_id, 'Введите название города своего визави: ')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                city_name = event.text
                id_city = self.cities(user_id, city_name)
                if id_city != '' or id_city != None:
                    return str(id_city)
                else:
                    break

    # Запросить семейное положение визави
    def get_status(self, user_id):
        url_status = self.url + 'users.get'
        params = {'user_ids': user_id,
                  'fields': 'status'}
        response = requests.get(url_status, params={**self.params, **params}).json()

        self.write_msg(user_id, 'Семейной вашего визави, выберите из списка\n'
                                         '1 — не женат (не замужем)\n'
                                         '2 — встречается\n'
                                         '3 — помолвлен(-а)\n'
                                         '4 — женат(замужем)\n'
                                         '5 — всё сложно\n'
                                         '6 — в активном поиске\n'
                                         '7 — влюблен(-а)\n'
                                         '8 — в гражданском браке \n')

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                status = event.text
                return status

    # Поиск визави по запрошенным данным
    def find_user(self, user_id):
        url_search = self.url + 'users.search'
        params = {'v': '5.131',
                  'age_from': self.get_age_low(user_id),
                  'age_to': self.get_age_high(user_id),
                  'sex': self.get_sex(user_id),
                  'city': self.find_city(user_id),
                  'fields': 'is_closed, id, first_name, last_name',
                  'status': self.get_status(user_id),
                  'count': 500}
        response = requests.get(url_search, params={**self.params, **params}).json()
        try:
            dict_1 = response['response']
            list_1 = dict_1['items']
            for person_dict in list_1:
                if person_dict.get('is_closed') == False:
                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    vk_link = 'vk.com/id' + str(person_dict.get('id'))
                    insert_data_users(first_name, last_name, vk_id, vk_link)
                else:
                    continue
            return f'Поиск завершён'
        except KeyError:
            self.write_msg(user_id, 'Ошибка')



    # Добавление в черный список
    # !!!!!!!!!!!!попробовать через БД

    # Получить фотографии
    def get_photos_id(self, user_id):
        url_photos_id = self.url + 'photos.get'
        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 'likes',
            'photo_sizes': '1',
            'count': 25
        }
        response = requests.get(url_photos_id, params={**self.params, **params}).json()

        photos = dict()
        try:
            for info_user in response['response']['items']:
                photo_id = str(info_user.get('id'))
                i_likes = info_user.get('likes')
                if i_likes.get('count'):
                    likes = i_likes.get('count')
                    photos[likes] = photo_id
            list_of_ids = sorted(photos.items(), reverse=True)
            return list_of_ids
        except KeyError:
            self.write_msg(user_id, 'Ошибка')

    # Фото номер 1
    def get_photo_1(self, user_id):
        list = self.get_photos_id(user_id)
        count = 0
        for photo_user in list:
            count += 1
            if count == 1:
                return photo_user[1]

    # Фото номер 2
    def get_photo_2(self, user_id):
        list = self.get_photos_id(user_id)
        count = 0
        for photo_user in list:
            count += 1
            if count == 2:
                return photo_user[1]

    # Фото номер 3
    def get_photo_3(self, user_id):
        list = self.get_photos_id(user_id)
        count = 0
        for photo_user in list:
            count += 1
            if count == 3:
                return photo_user[1]

    # Отправить 1 фотографию
    def send_photo_1(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': TOKEN_GROUP,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(offset)}_{self.get_photo_1(self.person_id(offset))}',
                                         'random_id': 0})

    # Отправить 2 фотографию
    def send_photo_2(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': TOKEN_GROUP,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(offset)}_{self.get_photo_2(self.person_id(offset))}',
                                         'random_id': 0})

    # Отправить 3 фотографию
    def send_photo_3(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': TOKEN_GROUP,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(offset)}_{self.get_photo_3(self.person_id(offset))}',
                                         'random_id': 0})

    def find_persons(self, user_id, offset):
        self.write_msg(user_id, self.found_person_info(offset))
        self.person_id(offset)
        insert_data_seen_users(self.person_id(offset), offset)  # offset
        insert_data_favorites(self.person_id(offset), offset)  # favorites
        self.get_photos_id(self.person_id(offset))
        self.send_photo_1(user_id, 'Фото номер 1', offset)
        if self.get_photo_2(self.person_id(offset)) != None:
            self.send_photo_2(user_id, 'Фото номер 2', offset)
            self.send_photo_3(user_id, 'Фото номер 3', offset)
        else:
            self.write_msg(user_id, f'Больше фотографий нет')

    # Инфа о визави
    def found_person_info(self, offset):
        info_person = select(offset)
        list_person = []
        for user in info_person:
            list_person.append(user)
            if {list_person[3]} not in self.user_favorites(self): # Исключение из просмотра
                return f'{list_person[0]} {list_person[1]}, ссылка - {list_person[3]}' # Исключение из просмотра
        return f'{list_person[0]} {list_person[1]}, ссылка - {list_person[3]}'

    # ИД визави
    def person_id(self, offset):
        info_person = select(offset)
        list_person = []
        for id in info_person:
            list_person.append(id)
        return str(list_person[2])

    # Добавить в избранное
    def user_favorites(self, offset):
        info_person = select(offset)
        list_person = []
        for id in info_person:
            list_person.append(id)
        return str(list_person[2])


    # Не работает, хоть тресни...
    # if __name__ == '__main__':
    #     Base.metadata.create_all(engine)


bot = VKBot()
