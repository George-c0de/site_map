from rest_framework.test import APITestCase
from django.urls import reverse

from site_map.models import Profile


class AccountTests(APITestCase):
    def test_add_profile(self):
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
            'number': '1234567890987654321234567890987654321234',
            'orthokeratological_lenses_1': 'Contex',
            'customized_orthokeratological_lenses_1': 'RGP Designer',
            'scleral_lenses': 'OKVision SMARTFIT'
        }
        url = reverse('register')
        # Создание пользователя с номеров больше 30
        self.client.post(url, data_user, format='json')
        self.assertEqual(Profile.objects.count(), 0)
        print('OK')
        data_user['number'] = '+76878'
        data_user['password1'] = '123'
        data_user['password2'] = '123'
        # Создание с некорректным паролем
        self.client.post(url, data_user, format='json')
        self.assertEqual(Profile.objects.count(), 0)
        print('OK')
        data_user['standard_soft'] = 'Неверный выбор'
        # Создание с неверным выбором
        self.client.post(url, data_user, format='json')
        self.assertEqual(Profile.objects.count(), 0)
        print('OK')

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
            'scleral_lenses_1': 'OKVision SMARTFIT'
        }
        url = reverse('register')
        self.client.post(url, data_user, format='json')
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.get().user.email, 'email@yandex.ru')
        print('OK! Create User')
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
        url = reverse('get_coords_and_profile')
        requests = self.client.get(url)
        data = requests.data['features'][0]['geometry']['coordinates']
        self.assertEqual(data, [
            '40.00000000000000',
            '40.00000000000000'
        ])
