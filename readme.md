# Сайт Django c интеграцией yandex.map

## Оглавление

* [Общая информация](#общая-информация)
* [Технологии](#технологии)
    * [Библиотеки](#библиотеки)
    * [Тесты](#тесты)
    * [Рассылка](#рассылка)
* [Настройка](#Настройка)
    * [Файл env](#env)
    * [Миграции](#Миграции)
    * [БД PostgresSQL](#PostgresSQL)

## Общая информация

Сайт по поиску специалистов, с возможностью фильтрации и поиска по карте

**Для специалиста:**

1. Выбор мест, где специалист хочет принимать
2. Указание линз, с которыми работает
3. Отправка логина и пароля на почту

**Для обычного пользователя:**

1. Поиск и фильтрация специалиста на карте

#### Домашняя страница

<img src="media\home-page.svg" width="1920" height="400" alt="Главная страница"  title="Главная страница">

#### Личный кабинет

<img src="media\lk1.svg" width="1920" height="400" title="Личный кабинет" alt="Личный кабинет">
<br>
<img src="media\lk2.svg" width="1920" height="400" title="Личный кабинет" alt="Личный кабинет">

## Технологии

### Библиотеки

Этот проект написан на Django с использованием следующих библиотек:

+ Pillow
+ djangorestframework
+ sendsay-api-python
+ psycopg2
+ requests
+ django-environ

### Тесты

Проект имеет unit тесты для проверки:

1. Корректность создания пользователя
2. Правильное добавление точек на карту
3. Получение координат специалиста

### Рассылка

Отправка данных пользователя выполнена с помощью сервиса "sendsay"

Функция

```
def send_message(password=env('SENDSAY_PASSWORD'),
        login_sendsay=env('SENDSAY_LOGIN'),
        email_sender=env('SENDSAY_EMAIL'),
        password_user=None,
        email_user=None)
```

* password - Пароль SENDSAY
* login_sendsay - Логин SENDSAY
* email_sender - Почта отправителя
* password_user - Пароль пользователя
* email_user - Почта пользователя

### Работа с картами яндекс

Вся работа с яндекс картами выполнена с помощью API Яндекс.Карт, а также с api проекта

* Получение точек

```
def get_coords_and_profile(request)
```

* Добавление точек

```
def delete_coords(request)
```

* Получение фильтров

```
def get_filter(request)
```

## Настройка

### PostgresSQL

В файле settings директория site_map

Поле DATABASES:
NAME - Имя бд
USER - Пользователь
PASSWORD - Пароль
PORT - Порт(default 5432)

### env

Чтобы запустить проект, нужно добавить в корневую директорию файл env, который должен содержать 6 полей:

1. SECRET_KEY - секретный ключ Django
2. DEBUG - значение дебагера
3. SENDSAY_LOGIN - Логин от SENDSAY
4. SENDSAY_EMAIL- Почта от SENDSAY
5. SENDSAY_PASSWORD - Пароль от SENDSAY
6. YANDEX_MAP - Ключ от Яндекс карт

### Миграции

После добавления файла нужно сделать миграцию с помощью двух команд

1. python manage.py makemigrations
2. python manage.py migrate      




