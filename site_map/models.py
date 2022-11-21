from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import re


class Image(models.Model):
    image = models.ImageField('/', blank=True)

    def __str__(self):
        print(self.image.name)
        if self.image.name is not None and self.image.name != '':
            return self.image.name
        else:
            return f"name"

    class Meta:
        verbose_name_plural = _("Изображения")


def validate_even(value):
    result = re.match(r'(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){1,30}(\s*)?', value)
    if result is None or len(value) > 30 or len(value) == 0:
        raise ValidationError(
            _('%(value)s is not an even number'),
            params={'value': value},
        )


class Profile(models.Model):
    YES_OR_NO = [
        ('YES', 'YES'),
        ('NO', 'NO')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.OneToOneField(Image, on_delete=models.CASCADE, null=True, blank=True)
    patronymic = models.CharField('Отчество', max_length=150, blank=True)
    position = models.CharField('Должность', max_length=150)
    specialized_training = models.CharField('Специализированное обучение по контактной коррекции', max_length=150,
                                            null=True, blank=True)
    standard_soft = models.CharField('Cтандартные мягкие контактные линзы', max_length=50, choices=YES_OR_NO)
    standard_soft_for_myopia = models.CharField('Специальные мягкие контактные линзы для контроля миопии',
                                                max_length=50, choices=YES_OR_NO)
    customized_soft_contact_lenses = models.CharField('Индивидуальные мягкие контактные линзы',
                                                      max_length=50, choices=YES_OR_NO)
    soft_contact_lenses_for_keratoconus = models.CharField('Мягкие контактные линзы для кератоконуса',
                                                           max_length=50, choices=YES_OR_NO)

    # orthokeratological_lenses = models.CharField('Ортокератологические линзы c фиксированным дизайном', max_length=50)

    # customized_orthokeratological_lenses = models.CharField('Кастомизированные ортокератологические линзы',
    # max_length=50)

    corneal_rigid = models.CharField('Роговичные жесткие газопроницаемые контактные линзы',
                                     max_length=50, choices=YES_OR_NO)
    # scleral_lenses = models.CharField('Склеральные линзы', max_length=150, null=True, blank=True)

    description = models.CharField('Дополнительная информация об опыте в контактной коррекции', max_length=200,
                                   null=True, blank=True)
    number = models.CharField('Контактный телефон для коллег', max_length=50, validators=[validate_even])

    def __str__(self):
        return f"{self.user.email.capitalize()}"

    class Meta:
        verbose_name_plural = _("Пользователь")


class ScleralLenses(models.Model):
    name = models.CharField('Название', max_length=150)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"Name: {self.name}, User: {self.user.user.email}"

    class Meta:
        verbose_name_plural = _("Склеральные линзы")


class CustomizedOrthokeratologicalLenses(models.Model):
    name = models.CharField('Название', max_length=150)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"Name: {self.name}, User: {self.user.user.email}"

    class Meta:
        verbose_name_plural = _("Кастомизированные ортокератологические линзы")


class OrthokeratologyFixedDesignLenses(models.Model):
    name = models.CharField('Название', max_length=150)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"Name: {self.name}, User: {self.user.user.email}"

    class Meta:
        verbose_name_plural = _("Ортокератологические линзы с фиксированным дизайном")


class Coords(models.Model):
    address = models.CharField('Адрес', max_length=150, default='')
    coords_x = models.DecimalField('X', max_digits=20, decimal_places=15)
    coords_y = models.DecimalField('Y', max_digits=20, decimal_places=15)
    filter_coords = models.CharField('Фильтр', max_length=150, default='')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.coords_x}, {self.coords_y}, User: {self.user.user.email}"

    class Meta:
        verbose_name_plural = _("Координаты пользователей")
