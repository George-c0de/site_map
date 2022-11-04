import json

from django.test import TestCase

from rest_framework.test import force_authenticate, APITestCase
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework import status

from site_map.models import Profile


class AccountTests(APITestCase):
    def test_create_account(self):
        data_user = {
            'username': 'email@yandex.ru',
            'email': 'email@yandex.ru',
            'password1': '12345678QWER',
            'password2': '12345678QWER',
            'first_name': '',
            'last_name': '',
            'image': None,
            'patronymic': '',
            'position': 'Офт',
            'specialized_training': '2',
            'standard_soft': 'YES',
            'standard_soft_for_myopia': 'YES',
            'customized_soft_contact_lenses': 'YES',
            'soft_contact_lenses_for_keratoconus': 'YES',
            'corneal_rigid': 'YES',
            'description': 'other',
            'number': '+748758947',
            'orthokeratological_lenses_1': 'Contex',
            'customized_orthokeratological_lenses_1': 'RGP Designer',
            'scleral_lenses': 'OKVision SMARTFIT'
        }
        url = reverse('register')
        request = self.client.post(url, data_user, format='json')
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.get().user.email, 'email@yandex.ru')
        self.add_coords()
        self.get_coords()

    def add_coords(self):
        url = reverse('add_coord')
        data = {
            'address': 'г. Москва',
            'coords_x': '40',
            'coords_y': '40',
            'filter_coords': 'Москва'
        }
        self.client.post(url, data, follow='json')

    def get_coords(self):
        profile = Profile.objects.get()
        url = reverse('get_coords_and_profile')
        requests = self.client.get(url)
        data = requests.data['features'][0]['geometry']['coordinates']
        self.assertEqual(data, [
            '40.00000000000000',
            '40.00000000000000'
        ])
