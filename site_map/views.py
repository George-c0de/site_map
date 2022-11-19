import os
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sendsay.api import SendsayAPI
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from project.settings import env, YANDEX_MAP
from .forms import *
from .models import *
import logging
import re
from rest_framework import status

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
        if user.photo.image.name:
            delete_image = Image.objects.get(id=user.photo.id)
            os.remove(delete_image.image.path)
            user.photo = None
            user.save()
            delete_image.delete()
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
    if user.check_password(new_password):
        return ''
    if new_password == '' or new_password is None:
        return ''
    if new_password is None:
        return 'Пароль не соответствует требованиям'
    else:
        user.set_password(new_password)
        user.save()
    return new_password


def save_change_map(user, coords, name, map_filter):
    error_list = [None, '', ',']
    if coords in error_list:
        return None
    coords = coords.split(',')
    if len(coords) != 2:
        return None
    for el in range(0, len(coords)):
        coords[el] = Decimal(coords[el])
    map_coords = Coords(
        coords_x=coords[0],
        coords_y=coords[1],
        name=name,
        filter_coords=map_filter,
        user=user
    ).save()
    return map_coords


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


@api_view(['GET'])
def get_filter(request):
    """
    :param request:
    :return: Возвращает список для фильтрации данных на карте
    """
    coords = Coords.objects.all()
    result_end = {
        'city': [],
        'position': [],
        'standard_soft': [],
        'standard_soft_for_myopia': [],
        'customized_soft_contact_lenses': [],
        'soft_contact_lenses_for_keratoconus': [],
        'corneal_rigid': [],
        'scleral_lenses': [],
        'orthokeratological_lenses': [],
        'customized_orthokeratological_lenses': []

    }
    for el in coords:
        profile = Profile.objects.get(id=el.user.id)
        if el.filter_coords not in result_end['city']:
            result_end['city'].append(el.filter_coords.capitalize())
        if profile.position not in result_end['position']:
            result_end['position'].append(profile.position.capitalize())
        if profile.standard_soft.upper() not in result_end['standard_soft']:
            result_end['standard_soft'].append(profile.standard_soft.upper())
        if profile.standard_soft_for_myopia.upper() not in result_end['standard_soft_for_myopia']:
            result_end['standard_soft_for_myopia'].append(profile.standard_soft_for_myopia.upper())
        if profile.customized_soft_contact_lenses.upper() not in result_end['customized_soft_contact_lenses']:
            result_end['customized_soft_contact_lenses'].append(profile.customized_soft_contact_lenses.upper())
        if profile.soft_contact_lenses_for_keratoconus.upper() not in result_end['soft_contact_lenses_for_keratoconus']:
            result_end['soft_contact_lenses_for_keratoconus'].append(
                profile.soft_contact_lenses_for_keratoconus.upper())
        if profile.corneal_rigid.upper() not in result_end['corneal_rigid']:
            result_end['corneal_rigid'].append(profile.corneal_rigid.upper())

        orthokeratological_lenses = ScleralLenses.objects.filter(user=profile)

        for lenses in orthokeratological_lenses:
            if lenses.name.capitalize() not in result_end['scleral_lenses']:
                result_end['scleral_lenses'].append(lenses.name.capitalize())

        orthokeratological_lenses = OrthokeratologyFixedDesignLenses.objects.filter(user=profile)
        for lenses in orthokeratological_lenses:
            if lenses.name.capitalize() not in result_end['orthokeratological_lenses']:
                result_end['orthokeratological_lenses'].append(lenses.name.capitalize())

        customized_orthokeratological_lenses = CustomizedOrthokeratologicalLenses.objects.filter(user=profile)
        for lenses in customized_orthokeratological_lenses:
            if lenses.name.capitalize() not in result_end['customized_orthokeratological_lenses']:
                result_end['customized_orthokeratological_lenses'].append(lenses.name.capitalize())

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
        profile = Profile.objects.get(id=el.user.id)
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
        all_scleral_lenses = ScleralLenses.objects.filter(user=profile)
        scleral_lenses = []
        for le in all_scleral_lenses:
            scleral_lenses.append(le.name.capitalize())
        all_orthokeratological_lenses = OrthokeratologyFixedDesignLenses.objects.filter(user=profile)

        orthokeratological_lenses = []
        for le in all_orthokeratological_lenses:
            orthokeratological_lenses.append(le.name.capitalize())
        all_customized_orthokeratological_lenses = CustomizedOrthokeratologicalLenses.objects.filter(user=profile)
        customized_orthokeratological_lenses = []
        for cust in all_customized_orthokeratological_lenses:
            customized_orthokeratological_lenses.append(cust.name.capitalize())
        filters = {
            'position': profile.position,
            'standard_soft': profile.standard_soft,
            'standard_soft_for_myopia': profile.standard_soft_for_myopia,
            'customized_soft_contact_lenses': profile.customized_soft_contact_lenses,
            'soft_contact_lenses_for_keratoconus': profile.soft_contact_lenses_for_keratoconus,
            'corneal_rigid': profile.corneal_rigid,
            'scleral_lenses': scleral_lenses,
            'orthokeratological_lenses': orthokeratological_lenses,
            'customized_orthokeratological_lenses': customized_orthokeratological_lenses,
            'city': el.filter_coords.capitalize()
        }

        pattern_point_properties = {
            "balloonContent": filters,
            "clusterCaption": f"{el.filter_coords}"
        }
        x = json.dumps(el.coords_x, cls=DecimalEncoder)[1:-2]
        y = json.dumps(el.coords_y, cls=DecimalEncoder)[1:-2]
        point['geometry']['coordinates'] = [x, y]  # Координаты
        pattern_point_properties['balloonContentHeader'] = f'{el.address} <br>'
        # pattern_point_properties[
        #     'balloonContentHeader'] = f'<b>ФИО: </b>{user.last_name} {user.first_name} {profile.patronymic}'
        if profile.photo.image.name != '':
            image = profile.photo.image.url
        else:
            image = ''
        image_html = f'<img class="cover" alt="картинка" src="{image}">'
        fio_html = f'<b>ФИО: </b>{user.last_name} {user.first_name} {profile.patronymic}'
        # email_html = f'<b>Email: </b>{user.email}'
        # Содержимое точки на карте

        # description = f'{image_html} <br/><br/> {email_html}<br/>{fio_html}<br/><b>Адрес: </b>{el.address}'
        description = f'{image_html} <br/><br/> {fio_html}<br/><b>Адрес: </b>{el.address}'
        description += f'<br/><b>Должность:</b> {profile.position}'

        specialized_training = profile.specialized_training
        description += f'<br/><b>Специализированное обучение по контактной коррекции:</b> {specialized_training}'
        description += f'<br/><b>Cтандартные мягкие контактные линзы:</b> {get_yes_or_no(profile.standard_soft)}<br/>'

        standard_soft_for_myopia = get_yes_or_no(profile.standard_soft_for_myopia)
        description += f'<b>Специальные мягкие контактные линзы для контроля миопии:</b> {standard_soft_for_myopia}'

        customized_soft_contact_lenses = get_yes_or_no(profile.customized_soft_contact_lenses)
        description += f'<br/><b>Индивидуальные мягкие контактные линзы:</b> {customized_soft_contact_lenses}<br/>'
        soft_contact_lenses_for_keratoconus = get_yes_or_no(profile.soft_contact_lenses_for_keratoconus)

        description += f'<b>Мягкие контактные линзы для кератоконуса:</b> {soft_contact_lenses_for_keratoconus}<br/>'

        corneal_rigid = get_yes_or_no(profile.corneal_rigid)
        description += f'<b>Роговичные жесткие газопроницаемые контактные линзы:</b> {corneal_rigid}<br/>'

        description += f'<b>Дополнительная информация об опыте в контактной коррекции:</b> {profile.description}'

        description += f'<br/><b>Склеральные линзы:</b> '
        if ScleralLenses.objects.filter(user=profile).exists():
            for lenses in ScleralLenses.objects.filter(user=profile):
                description += lenses.name.capitalize() + ', '
            description = description[:-2]
        else:
            description += ' Нет'
        description += '<br/><b>Ортокератологические линзы c фиксированным дизайном:</b> '
        if OrthokeratologyFixedDesignLenses.objects.filter(user=profile).exists():
            for lenses in OrthokeratologyFixedDesignLenses.objects.filter(user=profile):
                description += lenses.name.capitalize() + ', '
            description = description[:-2]
        else:
            description += ' Нет'

        description += '<br/><b>Кастомизированные ортокератологические линзы:</b> '
        if CustomizedOrthokeratologicalLenses.objects.filter(user=profile).exists():
            for lenses in CustomizedOrthokeratologicalLenses.objects.filter(user=profile):
                description += lenses.name.capitalize() + ', '
            description = description[:-2]
        else:
            description += ' Нет'
        # description += '<br/>'

        pattern_point_properties['balloonContentBody'] = description
        # pattern_point_properties['balloonContentFooter'] = f'Информация предоставлена:<br/>OOO "Ваша организация"'
        pattern_point_properties['hintContent'] = f'<img alt="картинка" src="{image}" height="100" width="100" >'
        point['properties'] = pattern_point_properties
        result_end['features'].append(point)
        i += 1
    return Response(data=result_end)


def get_yes_or_no(prop):
    if prop.upper() == 'YES':
        return 'Да'
    else:
        return 'Нет'


def get_message(
        request,
        first_name,
        last_name,
        patronymic,
        image,
        password,
        email,
        description,
        position,
        specialized_training,
        scleral_lenses,
        orthokeratological_lenses,
        customized_orthokeratological_lenses,
        number
):
    if first_name != '':
        messages.success(request, 'Имя изменено')
    if last_name != '':
        messages.success(request, 'Фамилия изменена')
    if patronymic != '':
        messages.success(request, 'Отчество изменено')
    if image is not None:
        messages.success(request, 'Фотография изменена')
    if email == 'Email уже существует':
        messages.success(request, 'Email уже существует')
    elif email == 'Email указан неверно':
        messages.success(request, 'Email указан неверно')
    elif email != '':
        messages.success(request, 'Почта изменена')
    if password == 'Пароль не соответствует требованиям':
        messages.error(request, 'Пароль не соответствует требованиям')
    elif password != '':
        messages.success(request, 'Пароль изменен')
    if description is not None:
        messages.success(request, 'Дополнительная информация об опыте в контактной коррекции изменена')
    if position is not None:
        messages.success(request, 'Должность изменена')
    if specialized_training is not None:
        messages.success(request, 'Специализированное обучение по контактной коррекции изменено')
    if scleral_lenses is not None:
        messages.success(request, 'Склеральные линзы изменены')
    if orthokeratological_lenses is not None:
        messages.success(request, 'Ортокератологические линзы c фиксированным дизайном изменены')
    if customized_orthokeratological_lenses is not None:
        messages.success(request, 'Кастомизированные ортокератологические линзы изменены')
    if number is not None:
        messages.success(request, 'Номер телефона изменен')
    return messages


def change_email(user, email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        return 'Email указан неверно'
    error_list = ['', None]
    if user.email == email or email in error_list:
        return ''
    elif User.objects.filter(email=email).exists():
        return 'Email уже существует'
    else:
        user.email = email
        user.username = email
        user.save()
        return email


@api_view(['GET', 'POST'])
def lk(request):
    if request.user.is_authenticated:
        user = request.user
        profile = Profile.objects.get(user=user)
        if request.method == 'POST':
            data = request.data
            data_user = {
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'patronymic': request.POST.get('patronymic'),
                'image': request.FILES.get('image'),
                'password': request.POST.get('password'),
                'email': request.POST.get('email'),
                'position': request.POST.get('position'),
                'specialized_training': data['specialized_training'],

                'standard_soft': data['standard_soft'],
                'standard_soft_for_myopia': data['standard_soft_for_myopia'],
                'customized_soft_contact_lenses': data['customized_soft_contact_lenses'],
                'soft_contact_lenses_for_keratoconus': data['soft_contact_lenses_for_keratoconus'],
                'corneal_rigid': data['corneal_rigid'],

                'description': data['description'],
                'number': data['number']
            }
            image = save_or_change_image(user=profile, image=data_user['image'])
            first_name = change_first_name(user=user, name=data_user['first_name'])
            last_name = change_last_name(user=user, name=data_user['last_name'])
            patronymic = change_patronymic(user=profile, name=data_user['patronymic'])
            password = change_password(user, data_user['password'])
            email = change_email(user, data_user['email'])
            change_yes_or_no(data, profile)
            description = change_description(data['description'], profile)
            position = change_position(data['position'], profile)
            specialized_training = change_specialized_training(data['specialized_training'], profile)
            # scleral_lenses = change_scleral_lenses(data, profile)
            scleral_lenses = get_scleral_lenses(data)
            change_and_save_lenses(
                lenses_names=scleral_lenses,
                model=ScleralLenses,
                profile=profile,
                form=CreateScleralLensesForm)
            number = change_number(data['number'], profile)

            orthokeratological_lenses = choice_orthokeratological_lenses(data)
            change_and_save_lenses(
                lenses_names=orthokeratological_lenses,
                model=OrthokeratologyFixedDesignLenses,
                profile=profile,
                form=CreateOrthokeratologyFixedDesignLensesForm)
            # change_and_save_orthokeratological_lenses(orthokeratological_lenses, profile)

            customized_orthokeratological_lenses = choice_customized_orthokeratological_lenses(data)
            change_and_save_lenses(
                lenses_names=customized_orthokeratological_lenses,
                model=CustomizedOrthokeratologicalLenses,
                profile=profile,
                form=CreateCustomizedOrthokeratologicalLensesForm)
            # change_and_save(customized_orthokeratological_lenses, profile)

            get_message(request=request, first_name=first_name, last_name=last_name, image=image, patronymic=patronymic,
                        password=password, email=email, description=description,
                        position=position, specialized_training=specialized_training,
                        scleral_lenses=scleral_lenses,
                        customized_orthokeratological_lenses=customized_orthokeratological_lenses,
                        orthokeratological_lenses=orthokeratological_lenses,
                        number=number,
                        )
            if password != '':
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        context = {
            'user': profile,
            'auth': request.user.is_authenticated,
            'coords': Coords.objects.filter(user=Profile.objects.get(user=user)),
            'customized_orthokeratological_lenses': CustomizedOrthokeratologicalLenses.objects.filter(user=profile),
            'YANDEX_MAP': YANDEX_MAP
        }
        return render(request, 'site_map/personal_area.html', context=context)
    else:
        return redirect('login')


def change_number(number, profile):
    try:
        validate_even(number)
        profile.number = number
        profile.save()
        return True
    except Exception as e:
        print(e)
    finally:
        return None


def change_description(description, profile):
    des = profile.description
    if des == description:
        return None
    else:
        profile.description = description
        profile.save()
        return True


def change_position(position, profile):
    pos = profile.position
    if pos == position:
        return None
    else:
        profile.position = position
        profile.save()
        return True


def change_specialized_training(specialized_training, profile):
    spec = profile.specialized_training
    if spec == specialized_training:
        return None
    else:
        profile.specialized_training = specialized_training
        profile.save()
        return True


def change_yes_or_no(data, profile):
    if data['standard_soft'] != str(0):
        profile.standard_soft = data['standard_soft']
    if data['standard_soft_for_myopia'] != str(0):
        profile.standard_soft_for_myopia = data['standard_soft_for_myopia']
    if data['customized_soft_contact_lenses'] != str(0):
        profile.customized_soft_contact_lenses = data['customized_soft_contact_lenses']
    if data['soft_contact_lenses_for_keratoconus'] != str(0):
        profile.soft_contact_lenses_for_keratoconus = data['soft_contact_lenses_for_keratoconus']
    if data['corneal_rigid'] != str(0):
        profile.corneal_rigid = data['corneal_rigid']
    profile.save()


def get_custom_or_orthokeratological(model, names, profile):
    result = {}
    names = list(map(lambda x: x.upper(), names))
    other = 'Другое'.upper()
    for el in model.objects.filter(user=profile):
        if el.name.upper() in names:
            result[el.name.upper()] = True
        else:
            result[other] = el.name.upper()
    return result


@api_view(['GET'])
def get_info_lk(request):
    data = None
    if request.user.is_authenticated:
        user = request.user
        profile = Profile.objects.get(user=user)

        customized_orthokeratological_lenses = get_custom_or_orthokeratological(
            model=CustomizedOrthokeratologicalLenses,
            names=['RGP Designer', 'OrthoTool', 'Нет'],
            profile=profile)

        orthokeratological_lenses = get_custom_or_orthokeratological(
            model=OrthokeratologyFixedDesignLenses,
            names=['Contex', 'DL-ESA', 'Emerald', 'MoonLens', 'OKVision', 'Paragon CRT', 'нет'],
            profile=profile)
        scleral_lenses = get_custom_or_orthokeratological(
            model=ScleralLenses,
            names=['OKVision SMARTFIT', 'SkyOptix ZenLens', 'Нет'],
            profile=profile)
        data = {
            'auth': request.user.is_authenticated,
            'orthokeratological_lenses': orthokeratological_lenses,
            'customized_orthokeratological_lenses': customized_orthokeratological_lenses,
            'scleral_lenses': scleral_lenses
        }
    return Response(data=data, status=200)


@api_view(['GET', 'POST'])
def home_page(request):
    table_data = []
    i = 0
    for el in Coords.objects.all():
        i += 1
        table_data.append({
            'id': i,
            'fio': el.user.user.last_name + ' ' + el.user.user.first_name + ' ' + el.user.patronymic,
            'address': el.address
        })
    context = {
        'auth': request.user.is_authenticated,
        'table_data': table_data,
        'YANDEX_MAP': YANDEX_MAP
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
    api.request('issue.send', {
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
    return True


def add_coords(request):
    return render(request, 'site_map/add_coords.html', context={'YANDEX_MAP': YANDEX_MAP})


@csrf_exempt
def delete_coords(request):
    try:
        coords_id = request.POST.get('coords_id')
        if Coords.objects.filter(id=coords_id).exists():
            Coords.objects.get(id=coords_id).delete()
    except BaseException as e:
        print(e)
        return JsonResponse({'error': 'Some error'}, status=400)
    else:
        return JsonResponse({'error': 'Some error'}, status=200)


@csrf_exempt
def add_coord(request):
    try:
        address = request.POST.get('address')
        coords_x = request.POST.get('coords_x')
        coords_y = request.POST.get('coords_y')
        filter_coords = request.POST.get('filter_coords')
        list_error = ['', None]
        if address not in list_error and filter_coords not in list_error:
            Coords.objects.create(
                address=address,
                coords_x=coords_x,
                coords_y=coords_y,
                filter_coords=filter_coords,
                user=Profile.objects.get(user=request.user)
            ).save()
        else:
            return JsonResponse({'error': 'Some error'}, status=400)
    except BaseException as e:
        print(e)
        return JsonResponse({'error': 'Some error'}, status=400)
    else:
        return JsonResponse({'error': 'Some error'}, status=200)


def get_scleral_lenses(data):
    scleral_lenses = []
    if data.get('scleral_lenses_1', False):
        scleral_lenses.append(data['scleral_lenses_1'])
    if data.get('scleral_lenses_2', False):
        scleral_lenses.append(data['scleral_lenses_2'])
    if data.get('scleral_lenses_3', False):
        return None
    if data.get('scleral_lenses_4', False):
        scleral_lenses.append(data['other_scleral_lenses'])
    return scleral_lenses


@api_view(['GET', 'POST'])
def register_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            data = request.data
            register_user = {
                'username': data['email'],
                'email': data['email'],
                'password1': data['password1'],
                'password2': data['password2'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
            }
            form = CreateUserForm(register_user)
            if form.is_valid():
                form.save()
                user, image, profile = None, None, None
                try:
                    user = User.objects.get(username=data['email'])
                    temp_image = request.FILES.get('image')
                    image = Image.objects.create(image=temp_image)
                    patronymic = data['patronymic']
                    if data['position'] == str(3):
                        position = data['other_position']
                    else:
                        position = data['position']
                    specialized_training = data['specialized_training']
                    standard_soft = data['standard_soft']
                    standard_soft_for_myopia = data['standard_soft_for_myopia']
                    customized_soft_contact_lenses = data['customized_soft_contact_lenses']
                    soft_contact_lenses_for_keratoconus = data['soft_contact_lenses_for_keratoconus']
                    corneal_rigid = data['corneal_rigid']
                    description = data['description']
                    number = data['number']
                    profile_data = {
                        'user': user,
                        'patronymic': patronymic,
                        'photo': image,
                        'position': position.capitalize(),
                        'specialized_training': specialized_training.upper(),
                        'standard_soft': standard_soft.upper(),
                        'standard_soft_for_myopia': standard_soft_for_myopia.upper(),
                        'customized_soft_contact_lenses': customized_soft_contact_lenses.upper(),
                        'soft_contact_lenses_for_keratoconus': soft_contact_lenses_for_keratoconus.upper(),
                        'corneal_rigid': corneal_rigid.upper(),
                        'description': description.capitalize(),
                        'number': number,
                    }
                    form_profile = CreateProfileForm(profile_data)
                    if form_profile.is_valid():
                        form_profile.save()
                        send_message(password_user=data['password1'], email_user=data['email'])
                        profile = Profile.objects.get(user_id=user.id)
                    else:
                        delete_all(user, image)
                        return render(request, 'site_map/register.html', status=status.HTTP_400_BAD_REQUEST,
                                      context={'YANDEX_MAP': YANDEX_MAP})
                    scleral_lenses = get_scleral_lenses(data)
                    if scleral_lenses is not None:
                        for el in scleral_lenses:
                            scleral_lenses_data = {
                                'name': el.capitalize(),
                                'user': profile
                            }
                            form_scleral_lenses = CreateScleralLensesForm(scleral_lenses_data)
                            if form_scleral_lenses.is_valid():
                                form_scleral_lenses.save()

                    orthokeratological_lenses = choice_orthokeratological_lenses(data)
                    if orthokeratological_lenses is not None:
                        for el in orthokeratological_lenses:
                            orthokeratological_lenses_data = {
                                'name': el.capitalize(),
                                'user': profile
                            }
                            form_orthokeratology = CreateOrthokeratologyFixedDesignLensesForm(
                                orthokeratological_lenses_data)
                            if form_orthokeratology.is_valid():
                                form_orthokeratology.save()
                    customized_orthokeratological_lenses = choice_customized_orthokeratological_lenses(data)
                    if customized_orthokeratological_lenses is not None:
                        for el in customized_orthokeratological_lenses:
                            customized_orthokeratological_lenses_data = {
                                'name': el.capitalize(),
                                'user': profile
                            }
                            form_customized = CreateCustomizedOrthokeratologicalLensesForm(
                                customized_orthokeratological_lenses_data)
                            if form_customized.is_valid():
                                form_customized.save()
                    messages.success(request, 'Аккаунт создан, ' + user.username)
                    if not request.user.is_authenticated:
                        user = authenticate(request, username=user.username, password=register_user['password1'])
                        login(request, user)
                    return redirect('add_coords')
                except BaseException as e:
                    print(e)
                    delete_all(user, image, profile)
                    return render(request, 'site_map/register.html', status=status.HTTP_400_BAD_REQUEST,
                                  context={'YANDEX_MAP': YANDEX_MAP})
            else:
                for count, value in enumerate(form.errors, start=0):
                    if value == 'username':
                        messages.error(request, 'Аккаунт с таким Email уже существует\n')
                    elif value == 'password2':
                        messages.error(request, 'Пароль не соответствует требованиям\n')
                    elif value == 'password1':
                        messages.error(request, 'Пароль не соответствует требованиям\n')
                # messages.error(request, form.errors)
                return render(request, 'site_map/register.html', status=status.HTTP_400_BAD_REQUEST,
                              context={'YANDEX_MAP': YANDEX_MAP})
        return render(request, 'site_map/register.html', context={'YANDEX_MAP': YANDEX_MAP})


def choice_customized_orthokeratological_lenses(data):
    customized_orthokeratological_lenses = []
    if data.get('customized_orthokeratological_lenses_1', False):
        customized_orthokeratological_lenses.append(data['customized_orthokeratological_lenses_1'])
    if data.get('customized_orthokeratological_lenses_2', False):
        customized_orthokeratological_lenses.append(data['customized_orthokeratological_lenses_2'])
    if data.get('customized_orthokeratological_lenses_3', False):
        return None
    if data.get('customized_orthokeratological_lenses_4', False):
        customized_orthokeratological_lenses.append(data['other_customized_orthokeratological_lenses'])
    return customized_orthokeratological_lenses


def change_and_save_lenses(lenses_names, model, profile, form):
    if lenses_names is not None:
        lenses_names = list(map(lambda x: x.upper(), lenses_names))
        profile_lenses = model.objects.filter(user=profile)
        delete_id = []
        save_lenses = []

        for el in profile_lenses:
            if el.name.upper() not in lenses_names:
                el.delete()
        for i, lenses in enumerate(lenses_names):
            for prof in profile_lenses:
                if lenses == prof.name.upper():
                    delete_id.append(i)
        delete_id.reverse()
        for i in delete_id:
            lenses_names.pop(i)

        for el in lenses_names:
            lenses_data = {
                'name': el,
                'user': profile
            }
            save_lenses.append(lenses_data)
        for el in save_lenses:
            form_lenses = form(el)
            if form_lenses.is_valid():
                form_lenses.save()
    else:
        for el in model.objects.filter(user=profile):
            el.delete()
        form_lenses = form({
            'name': 'нет'.capitalize(),
            'user': profile
        })
        if form_lenses.is_valid():
            form_lenses.save()


def choice_orthokeratological_lenses(data):
    orthokeratological_lenses = []
    if data.get('orthokeratological_lenses_1', False):
        orthokeratological_lenses.append(data['orthokeratological_lenses_1'])
    if data.get('orthokeratological_lenses_2', False):
        orthokeratological_lenses.append(data['orthokeratological_lenses_2'])
    if data.get('orthokeratological_lenses_3', False):
        orthokeratological_lenses.append(data['orthokeratological_lenses_3'])
    if data.get('orthokeratological_lenses_4', False):
        orthokeratological_lenses.append(data['orthokeratological_lenses_4'])
    if data.get('orthokeratological_lenses_5', False):
        orthokeratological_lenses.append(data['orthokeratological_lenses_5'])
    if data.get('orthokeratological_lenses_6', False):
        orthokeratological_lenses.append(data['orthokeratological_lenses_6'])
    if data.get('orthokeratological_lenses_7', False):
        return None
    if data.get('orthokeratological_lenses_8', False):
        orthokeratological_lenses.append(data['other_orthokeratological_lenses'])
    return orthokeratological_lenses
