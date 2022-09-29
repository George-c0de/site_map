import time
from decimal import Decimal

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
from project.settings import BASE_DIR
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
            image_save = Image(image=image)
            image_save.save()
            user.photo = image_save
            user.photo.save()
            user.save()
        else:
            image_save = Image()
            image_save.image = image
            image_save.save()
            user.photo = image
            user.save()
        return image_save
    else:
        return None


def change_first_name(user, name):
    user.first_name = name
    user.save()


def change_last_name(user, name):
    user.last_name = name
    user.save()


def change_patronymic(user, name):
    user.patronymic = name
    user.save()


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
    coords_profile = Coords(coords_x=coords[0], coords_y=coords[1], name=name)
    coords_profile.save()
    user.card = coords_profile
    user.save()
    return coords_profile


@api_view(['GET'])
def get_register(request):
    coords = Coords.objects.all()
    result_x = ''
    result_y = ''
    result_names = ''
    for el in coords:
        result_x += str(el.coords_x) + ','
        result_y += str(el.coords_y) + ','
        result_names += str(el.name) + '/'
    result_x = result_x[:-1]
    result_y = result_y[:-1]
    result_names = result_names[:-1]
    context = {
        'x': result_x,
        'y': result_y,
        'names': result_names
    }
    # time.sleep(3000)
    a = Response(data=context)
    return Response(data=context)


@api_view(['GET'])
def lk(request):
    return render(request, 'site_map/personal_area.html')


def home_page(request):
    coords = Coords.objects.all()
    result_x = ''
    result_y = ''
    result_names = ''
    for el in coords:
        result_x += str(el.coords_x) + ','
        result_y += str(el.coords_y) + ','
    context = {
        'x': result_x,
        'y': result_y,
        'names': result_names
    }
    return render(request, 'site_map/home.html', context=context)


def register_page(request):
    user = None
    profile = None
    coords_profile = None
    image = None
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
