from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import gettext_lazy as _


class Image(models.Model):
    image = models.ImageField('/', blank=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.OneToOneField(Image, on_delete=models.CASCADE, null=True, blank=True)
    patronymic = models.CharField('Отчество', max_length=150, blank=True)

    class Meta:
        verbose_name_plural = _("Пользователь")


class Coords(models.Model):
    address = models.CharField('Адрес', max_length=150, default='')
    coords_x = models.DecimalField('X', max_digits=17, decimal_places=15)
    coords_y = models.DecimalField('Y', max_digits=17, decimal_places=15)
    filter_coords = models.CharField('Фильтр', max_length=150, default='')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Координаты пользователей")
