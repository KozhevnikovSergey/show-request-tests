import requests
import os
import subprocess
import pytest


@pytest.fixture(scope='class')
def start_and_kill_server():
    os.startfile(r'http_srv_x86-64.exe')
    yield
    subprocess.call("TASKKILL /F /IM http_srv_x86-64.exe")


@pytest.mark.usefixtures('start_and_kill_server')
class Test_DB_Users(object):
    url = 'http://localhost:8000/'
    headers = {"X-Auth-Name": "admin",
               "X-Auth-Token": "d82494f05d6917ba02f7aaa29689ccb444bb73f20380876cb05d1f37537b7892"}

    def test_get_help(self):
        """
        Получение справочной страницы.
        """
        req = requests.get(f'{self.url}', headers=self.headers)
        assert "GET" in req.text
        assert req.status_code == 200

    def test_get_users(self):
        """
        Проверяется на пустое значение и на наличие обязательного поля username в возврашаемом списке пользователей.
        """
        req = requests.get(f'{self.url}users', headers=self.headers)
        assert req.text, 'Вернулся пустой список'
        assert req.text[0].get('username', False), 'Отсутвует username(обязательное поле)'
        assert req.status_code == 200

    @pytest.mark.parametrize("user, status_code, message", [
        ('admin', 200, 'Не найдет пользователь admin'),
        ('fgd2321jjjabbsjjqsdc', 404, 'Неправильный статус код для несуществующего '
                                      'пользователя')
    ])
    def test_check_user_existence(self, user, status_code, message):
        """
        Проверка существование пользователя
        """
        req = requests.head(f'{self.url}users/{user}', headers=self.headers)
        assert req.status_code == status_code, message

    @pytest.mark.parametrize("data, status_code, message", [
        ({"username": "Name3", "password": "Pass3", "description": "Description3"}, 200,
         'Произошла ошибка при создание пользователя'),
        ({"password": "Pass3", "description": "Description3"}, 400,
         'Неправильный статус код для запроса с неправильными данными')
    ])
    def test_added_user(self, data, status_code, message):
        """
        Добавление пользователя
        """
        req = requests.post(f'{self.url}users', headers=self.headers, data=data)
        assert req.status_code == status_code, message
        if 'username' in data:
            # проверка что пользователь был создан, если переданны корректные данные
            req = requests.head(f'{self.url}users/{data["username"]}', headers=self.headers)
            assert req.status_code == 200, 'Пользователь не был создан'

    @pytest.mark.parametrize("user, status_code, message", [
        ('admin', 200, 'Не найдет пользователь admin'),
        ('fgd2321jjjabbsjjqsdc', 404, 'Неправильный статус код для несуществующего '
                                      'пользователя')
    ])
    def test_delete_user(self, user, status_code, message):
        """
        Удаление пользователя.
        """
        req = requests.delete(f'{self.url}users/{user}', headers=self.headers)
        assert req.status_code == status_code, message

    @pytest.mark.parametrize("user, data, status_code, message", [
        ('admin', {"username": "Name3", "password": "Pass3", "description": "Description3"}, 200,
         'Произошла ошибка при создание пользователя'),
        ('fafasfasdas', {"username": "Name5", "password": "Pass3", "description": "Description3"}, 400,
         'Неправильный статус код для запроса с неправильными данными')
    ])
    def test_change_user(self, user, data, status_code, message):
        """
        Изменение пользователя.
        """
        req = requests.head(f'{self.url}users/{user}', headers=self.headers, data=data)
        assert req.status_code == status_code, message
