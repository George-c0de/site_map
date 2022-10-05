from decimal import Decimal
from sendsay.api import SendsayAPI
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from project.settings import env
from .forms import *
from .models import *
import logging
import re

# Лог выводим на экран и в файл
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'имя пользователя и пароль неверный.')
        return render(request, 'site_map/login.html')


def logout_user(request):
    logout(request)
    return redirect('login')


def save_or_change_image(image, user):
    """
    :param image: Картинка для обновления/сохранения
    :param user: Пользователь
    :return: При успешной смене картинки и ее сохранении: возвращается сама картинка, иначе None
    """
    if image is not None:
        if user.photo is not None:
            delete_image = Image.objects.get(id=user.photo.id)
            delete_image.delete()
            user.photo = None
            image_save = Image(image=image)
            image_save.save()
            user.photo = image_save
            user.photo.save()
            user.save()
        else:
            image_save = Image()
            image_save.image = image
            image_save.save()
            user.photo = image_save
            user.save()
        return image_save
    else:
        return None


def change_first_name(user, name):
    if user.first_name == name:
        return ''
    user.first_name = name
    user.save()
    return user.first_name


def change_last_name(user, name):
    if user.last_name == name:
        return ''
    user.last_name = name
    user.save()
    return user.last_name


def change_patronymic(user, name):
    if user.patronymic == name:
        return ''
    user.patronymic = name
    user.save()
    return user.patronymic


def delete_all(*args):
    for el in args:
        if el is not None:
            el.delete()


def validate_by_regexp(password, pattern):
    """Валидация пароля по регулярному выражению."""
    if re.match(pattern, password) is None:
        return False
    else:
        return True


def password_verification(password):
    """

    :param password: Новый пароль
    :return: при успешной смене пароля возвращается сам пароль, иначе None
    """
    # Пароль должен иметь не меньше 8 символов, прописные и строчные символы
    pattern = r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
    if validate_by_regexp(password, pattern):
        return password
    else:
        return None


def change_password(user, new_password):
    new_password = password_verification(new_password)
    if new_password is None:
        return 'Пароль не соответствует требованиям'
    if user.check_password(new_password):
        return ''
    else:
        user.set_password(new_password)
        user.save()
    return new_password


def save_change_map(user, coords, name):
    error_list = [None, '', ',']
    if coords in error_list:
        return None
    coords = coords.split(',')
    if len(coords) != 2:
        return None
    for el in range(0, len(coords)):
        coords[el] = Decimal(coords[el])
    if user.card is not None:
        coords_user = Coords.objects.get(id=user.card.id)
        if coords_user.coords_x == coords[0] and coords_user.coords_y == coords[1]:
            return None
        coords_user.delete()
        coords_profile = Coords(coords_x=coords[0], coords_y=coords[1], name=name)
        coords_profile.save()
        user.card = coords_profile
        user.save()
    else:
        coords_profile = Coords(coords_x=coords[0], coords_y=coords[1], name=name)
        coords_profile.save()
        user.card = coords_profile
        user.save()
    return coords_profile


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


@api_view(['GET'])
def get_filter(request):
    """
    :param request:
    :return: Возвращает список для фильтрации данных на карте(По населенному пункту)
    """
    coords = Coords.objects.all()
    result_end = []
    for el in coords:
        if el.name.split(',')[1][1:] not in result_end:
            result_end.append(el.name.split(',')[1][1:])
    return Response(data=result_end)


@api_view(['GET'])
def get_coords_and_profile(request):
    coords = Coords.objects.all()
    result_end = {
        'type': 'FeatureCollection',
        'features': []
    }
    i = 0
    for el in coords:
        profile = Profile.objects.get(card=el)
        user = profile.user
        # Шаблон для точки на карте
        point = {
            "id": i,
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "options": {
                    "preset": {
                        "islands#yellowCircleDotIconWithCaption",
                    }
                }
            }
        }
        pattern_point_properties = {
            "balloonContent": f"{profile.card.name.split(',')[1][1:]}",
            "clusterCaption": f"{profile.card.name.split(',')[1][1:]}"
        }
        x = json.dumps(el.coords_x, cls=DecimalEncoder)[1:-2]
        y = json.dumps(el.coords_y, cls=DecimalEncoder)[1:-2]
        point['geometry']['coordinates'] = [x, y] # Координаты
        pattern_point_properties['balloonContentHeader'] = f'{profile.card.name} <br>'
        if profile.photo.image.name != '':
            image = profile.photo.image.url
        else:
            image = ''
        image_html = f'<img alt="картинка" src="{image}" height="150" width="200" class="scale">'
        fio_html = f'<b>ФИО: </b>{user.last_name} {user.first_name} {profile.patronymic}'
        email_html = f'<b>Email: </b>{user.email}'
        # Содержимое точки на карте
        pattern_point_properties[
            'balloonContentBody'] = f'{image_html} <br/> {email_html}<br/>{fio_html}<br/><b>Адрес: </b>{profile.card.name}'
        pattern_point_properties['balloonContentFooter'] = f'Информация предоставлена:<br/>OOO "Ваша организация"'
        pattern_point_properties[
            'hintContent'] = f'<img alt="картинка" src="{image}" height="100" width="100" >'
        point['properties'] = pattern_point_properties
        result_end['features'].append(point)
        i += 1
    return Response(data=result_end)


def get_message(request, first_name, last_name, patronymic, map_coords, image, password):
    if first_name != '':
        messages.success(request, 'Имя изменено')
    if last_name != '':
        messages.success(request, 'Фамилия изменена')
    if patronymic != '':
        messages.success(request, 'Отчество изменено')
    if map_coords is not None:
        messages.success(request, 'Данные карты изменены')
    if image is not None:
        messages.success(request, 'Фотография изменена')
    if password == 'Пароль не соответствует требованиям':
        messages.error(request, 'Пароль не соответствует требованиям')
    elif password != '':
        messages.success(request, 'Пароль изменен')
    return messages


@api_view(['GET', 'POST'])
def lk(request):
    if request.user.is_authenticated:
        user = request.user
        profile = Profile.objects.get(user=user)
        if request.method == 'POST':
            data_user = {
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'patronymic': request.POST.get('patronymic'),
                'map_coords': request.POST.get('map_coords'),
                'map_address': request.POST.get('map_address'),
                'image': request.FILES.get('image'),
                'password': request.POST.get('password')
            }
            coords_profile = save_change_map(profile, data_user['map_coords'], data_user['map_address'])
            image = save_or_change_image(user=profile, image=data_user['image'])
            first_name = change_first_name(user=user, name=data_user['first_name'])
            last_name = change_last_name(user=user, name=data_user['last_name'])
            patronymic = change_patronymic(user=profile, name=data_user['patronymic'])
            password = change_password(user, data_user['password'])
            get_message(request=request, first_name=first_name, last_name=last_name, map_coords=coords_profile,
                        image=image,
                        patronymic=patronymic, password=password)
        context = {
            'user': profile,
            'auth': request.user.is_authenticated
        }
        return render(request, 'site_map/personal_area.html', context=context)
    else:
        return redirect('login')


@api_view(['GET', 'POST'])
def home_page(request):
    context = {
        'auth': request.user.is_authenticated
    }
    return render(request, 'site_map/home.html', context=context)


def send_message(
        password=env('SENDSAY_PASSWORD'),
        login_sendsay=env('SENDSAY_LOGIN'),
        email_sender=env('SENDSAY_EMAIL'),
        password_user=None,
        email_user=None
):
    api = SendsayAPI(login=login_sendsay, password=password)
    response = api.request('issue.send', {
        'sendwhen': 'now',
        'letter': {
            'subject': "Регистрация",
            'from.name': "Служба поддержки",
            'from.email': f"{email_sender}",
            'message': {
                'html': f"Password: {password_user}\n Email: {email_user}"
            }
        },
        'relink': 1,
        'users.list': f"{email_user}",
        'group': 'masssending',
    })
    print(response)
    return True


def register_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            register_user = {
                'username': request.POST.get('email'),
                'email': request.POST.get('email'),
                'password1': request.POST.get('password1'),
                'password2': request.POST.get('password2'),
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
            }
            form = CreateUserForm(register_user)
            if form.is_valid():
                form.save()
                user, image, profile = None, None, None
                try:
                    user = User.objects.get(username=request.POST.get('email'))
                    temp_image = request.FILES.get('image')
                    image = Image.objects.create(image=temp_image)
                    patronymic = request.POST.get('patronymic')
                    profile_data = {
                        'user': user,
                        'patronymic': patronymic,
                        'card': None,
                        'photo': image
                    }
                    form_profile = CreateProfileForm(profile_data)
                    if form_profile.is_valid():
                        form_profile.save()
                        send_message(password_user=request.POST.get('password1'), email_user=request.POST.get('email'))
                        profile = Profile.objects.get(user_id=user.id)
                        save_change_map(profile, request.POST.get('map_coords'), request.POST.get('map_address'))
                    else:
                        delete_all(user, image)
                    messages.success(request, 'Аккаунт создан,' + user.username)
                    return redirect('login')
                except BaseException as e:
                    print(e)
                    delete_all(user, image, profile)
            else:
                messages.error(request, 'Ошибка при создании аккаунта')
                return render(request, 'site_map/register.html')
        return render(request, 'site_map/register.html')
