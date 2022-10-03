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
        context = {}
        return render(request, 'site_map/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


def save_or_change_image(image, user):
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


def save_change_map(user, coords, name):
    error_list = [None, '']
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
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)


@api_view(['GET'])
def get_filter(request):
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
        point['geometry']['coordinates'] = [x, y]
        pattern_point_properties['balloonContentHeader'] = f'{profile.card.name} <br>'
        if profile.photo.image.name != '':
            image = profile.photo.image.url
        else:
            image = ''
        image_html = f'<img alt="картинка" src="{image}" height="150" width="200" class="scale">'
        fio_html = f'<b>ФИО: </b>{user.last_name} {user.first_name} {profile.patronymic}'
        email_html = f'<b>Email: </b>{user.email}'
        pattern_point_properties[
            'balloonContentBody'] = f'{image_html} <br/> {email_html}<br/>{fio_html}<b>Адрес: </b>{profile.card.name}'
        pattern_point_properties['balloonContentFooter'] = f'Информация предоставлена:<br/>OOO "Ваша организация"'
        pattern_point_properties[
            'hintContent'] = f'<img alt="картинка" src="{image}" height="100" width="100" >'
        point['properties'] = pattern_point_properties
        result_end['features'].append(point)
        i += 1
    return Response(data=result_end)


def get_message(request, first_name, last_name, patronymic, map_coords, image):
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
                'image': request.FILES.get('image')
            }
            coords_profile = save_change_map(profile, data_user['map_coords'], data_user['map_address'])
            image = save_or_change_image(user=profile, image=data_user['image'])
            first_name = change_first_name(user=user, name=data_user['first_name'])
            last_name = change_last_name(user=user, name=data_user['last_name'])
            patronymic = change_patronymic(user=profile, name=data_user['patronymic'])
            get_message(request=request, first_name=first_name, last_name=last_name, map_coords=coords_profile,
                        image=image,
                        patronymic=patronymic)
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


@api_view(['GET'])
def send_message(
        request,
        password=env('SENDSAY_PASSWORD'),
        login_sendsay=env('SENDSAY_LOGIN'),
        email='tering123@yandex.ru',
        email_sender=env('SENDSAY_EMAIL')
):
    api = SendsayAPI(login=login_sendsay, password=password)
    response = api.request('issue.send', {
        'sendwhen': 'now',
        'letter': {
            'subject': "Subject",
            'from.name': "Tester",
            'from.email': f"{email_sender}",
            'message': {
                'html': "Sendsay API client test message<hr>Hello!"
            }
        },
        'relink': 1,
        'users.list': f"{email}",
        'group': 'masssending',
    })

    return Response(data=response, status=200)


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
