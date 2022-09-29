import os
import time
from decimal import Decimal
from time import sleep
from sendsay.api import SendsayAPI
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth import models
import random
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from project.settings import BASE_DIR, STATIC_URL, MEDIA_ROOT
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
    user.first_name = name
    user.save()
    return user.first_name


def change_last_name(user, name):
    user.last_name = name
    user.save()
    return user.last_name


def change_patronymic(user, name):
    user.patronymic = name
    user.save()
    return user.patronymic


def create_profile(data):
    pass


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


@api_view(['GET'])
def get_coords_and_profile(request):
    coords = Coords.objects.all()
    result_x = ''
    result_y = ''
    result_names = ''
    first_name = []
    email = []
    last_name = []
    patronymic = []
    image = []
    address = []
    for el in coords:
        profile = Profile.objects.get()
        user = profile.user
        email.append(user.email)
        address.append(profile.card.name)
        image.append(profile.photo.image.url)
        if user.first_name is None or user.first_name == '':
            first_name.append('Не указано')
        else:
            first_name.append(user.first_name)
        if user.last_name is None or user.last_name == '':
            last_name.append('Не указано')
        else:
            last_name.append(user.last_name)
        if profile.patronymic is None or profile.patronymic == '':
            patronymic.append('Не указано')
        else:
            patronymic.append(profile.patronymic)
        result_x += str(el.coords_x) + ','
        result_y += str(el.coords_y) + ','
        result_names += str(el.name) + '/'
    result_x = result_x[:-1]
    result_y = result_y[:-1]
    context = {
        'x': result_x,
        'y': result_y,
        'first_name': first_name,
        'email': email,
        'last_name': last_name,
        'patronymic': patronymic,
        'image': image,
        'address': address,
    }
    # time.sleep(3000)
    return Response(data=context)


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
            'user': profile
        }
        return render(request, 'site_map/personal_area.html', context=context)
    else:
        return redirect('login')


def home_page(request):
    context = {
        'auth': request.user.is_authenticated
    }
    return render(request, 'site_map/home.html', context=context)


def send_message(request, password=123, email='tering123@yandex.ru'):
    api = SendsayAPI(login='x_1663938921994862', password='E-;K9(4#/Z')
    response = api.request('issue.send', {
        'sendwhen': 'now',
        'letter': {
            'subject': "Subject",
            'from.name': "Tester",
            'from.email': "rodionlxlnest@gmail.com",
            'message': {
                'html': "Sendsay API client test message<hr>Hello!"
            }
        },
        'relink': 1,
        'users.list': f"{email}",
        'group': 'masssending',
    })


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
            # print(profile_register)
            form = CreateUserForm(register_user)
            if form.is_valid():
                form.save()
                user = User.objects.get(username=request.POST.get('email'))
                coords_profile = save_change_map(user, request.POST.get('map_coords'), request.POST.get('map_address'))
                temp_image = request.FILES.get('image')
                image = Image.objects.create(image=temp_image)
                patronymic = request.POST.get('patronymic')
                profile_data = {
                    'user': user,
                    'patronymic': patronymic,
                    'card': coords_profile,
                    'photo': image
                }
                form_profile = CreateProfileForm(profile_data)
                if form_profile.is_valid():
                    form_profile.save()


                else:
                    delete_all(user, coords_profile, image)
                messages.success(request, 'Аккаунт создан,' + user.username)
                return redirect('login')
            else:
                messages.error(request, 'Ошибка при создании аккаунта')
                return render(request, 'site_map/register.html')
        return render(request, 'site_map/register.html')
