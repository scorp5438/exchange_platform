from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Ad, Category, ExchangeProposal


class AdsAppApiViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = {
            'username': 'TestAdminUser',
            'password': 'qwerty',
            'is_staff': True
        }
        cls.user_1 = {
            'username': 'TestUse_1',
            'password': 'qwerty'
        }
        cls.user_2 = {
            'username': 'TestUser_2',
            'password': 'qwerty'
        }

        cls.admin_user = User.objects.create_user(**cls.admin)
        cls.test_user_1 = User.objects.create_user(**cls.user_1)
        cls.test_user_2 = User.objects.create_user(**cls.user_2)

        cls.category_1 = Category.objects.create(
            category_name='pakipsi'
        )

        cls.category_2 = Category.objects.create(
            category_name='test category 2'
        )

        cls.ad_1 = Ad.objects.create(
            user=cls.admin_user,
            title='Test title 1',
            description='Test description 1',
            category=cls.category_1,
            condition='Новый',
        )

        cls.ad_2 = Ad.objects.create(
            user=cls.test_user_1,
            title='Test title 2',
            description='Test description 2',
            category=cls.category_1,
            condition='Новый',
        )

        cls.ad_3 = Ad.objects.create(
            user=cls.test_user_2,
            title='Another title 3',
            description='Test description 3',
            category=cls.category_2,
            condition='б/у',
        )

        cls.ad_4 = Ad.objects.create(
            user=cls.admin_user,
            title='Other title 4',
            description='Test description 4',
            category=cls.category_2,
            condition='б/у',
        )

        exp_props_1 = ExchangeProposal.objects.create(
            ad_sender=cls.ad_1,
            ad_receiver=cls.ad_2,
            comment='Test exp 1',
        )
        exp_props_2 = ExchangeProposal.objects.create(
            ad_sender=cls.ad_3,
            ad_receiver=cls.ad_4,
            comment='Test exp 2',
        )

    def test_ads_api_list(self):
        response = self.client.get(reverse('api-root:ads-list'))
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 4)
        self.assertEqual(response_data.get('results')[0].get('title'), 'Test title 1')
        self.assertEqual(response_data.get('results')[1].get('description'), 'Test description 2')

    def test_ad_api_in_id_exists(self):
        response = self.client.get(reverse(
            'api-root:ads-detail',
            kwargs={'pk': 1}
        ))
        status_code = response.status_code
        response_data = response.json()

        self.assertEqual(status_code, 200)
        self.assertEqual(response_data.get('id'), 1)
        self.assertEqual(response_data.get('description'), 'Test description 1')

    def test_ad_api_in_id_not_exists(self):
        response = self.client.get(reverse(
            'api-root:ads-detail',
            kwargs={'pk': 5}
        ))
        status_code = response.status_code
        response_data = response.json()

        self.assertEqual(status_code, 404)
        self.assertEqual(response_data.get('detail'), 'No Ad matches the given query.')

    def test_ads_api_with_filter_on_title(self):
        data = {'title': 'Test title 1'}

        response = self.client.get(
            reverse('api-root:ads-list'),
            data=data
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 1)
        self.assertEqual(response_data.get('results')[0].get('title'), 'Test title 1')

    def test_ads_api_with_filter_on_description(self):
        data = {'description': 'Test description 2'}

        response = self.client.get(
            reverse('api-root:ads-list'),
            data=data
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 1)
        self.assertEqual(response_data.get('results')[0].get('title'), 'Test title 2')

    def test_ads_api_with_filter_on_condition(self):
        data = {'condition': 'Новый'}

        response = self.client.get(
            reverse('api-root:ads-list'),
            data=data
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 2)
        self.assertEqual(response_data.get('results')[1].get('title'), 'Test title 2')

    def test_ads_api_with_filter_on_category(self):
        data = {'category': self.category_1.pk}

        response = self.client.get(
            reverse('api-root:ads-list'),
            data=data
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 2)
        self.assertEqual(response_data.get('results')[1].get('title'), 'Test title 2')

    def test_ads_api_with_search(self):
        data = {'search': 'pakipsi'}

        response = self.client.get(
            reverse('api-root:ads-list'),
            data=data
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 2)
        self.assertEqual(response_data.get('results')[0].get('title'), 'Test title 1')

    def test_create_ads_api(self):
        self.client.login(**self.user_1)
        data = {
            'condition': 'б/у',
            'category': self.category_2.pk,
            'title': 'A new title',
            'description': 'The new description',
        }

        response = self.client.post(
            reverse('api-root:ads-list'),
            data=data,
            content_type='application/json'
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data.get('message'), 'Ad created successfully')
        self.assertEqual(response_data.get('data').get('id'), 5)
        self.assertEqual(response_data.get('data').get('condition'), 'б/у')

        response = self.client.get(reverse('api-root:ads-list'))
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 5)

    def test_create_ads_api_not_exists_category(self):
        self.client.login(**self.user_1)
        data = {
            'condition': 'б/у',
            'category': 4,
            'title': 'A new title',
            'description': 'The new description',
        }

        response = self.client.post(
            reverse('api-root:ads-list'),
            data=data,
            content_type='application/json'
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('Недопустимый первичный ключ "4" - объект не существует.', response_data.get('category'))

    def test_update_ads_api_by_admin(self):
        self.client.login(**self.admin)
        data = {
            'description': 'Updated description',
        }

        response = self.client.patch(
            reverse(
                'api-root:ads-detail',
                kwargs={'pk': 2}
            ),
            data=data,
            content_type='application/json'
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('message'), 'Ad updated successfully')
        self.assertEqual(response_data.get('data').get('description'), 'Updated description')

    def test_update_ads_api_by_admin_not_exists(self):
        self.client.login(**self.admin)
        data = {
            'description': 'Updated description',
        }

        response = self.client.patch(
            reverse(
                'api-root:ads-detail',
                kwargs={'pk': 6}
            ),
            data=data,
            content_type='application/json'
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data.get('detail'), 'No Ad matches the given query.')

    def test_update_ads_api_by_user_not_self(self):
        self.client.login(**self.user_1)
        data = {
            'description': 'Updated description',
        }

        response = self.client.patch(
            reverse(
                'api-root:ads-detail',
                kwargs={'pk': 1}
            ),
            data=data,
            content_type='application/json'
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_data.get('detail'), 'Вы можете редактировать только свои объявления')

    def test_category_api_list(self):
        response = self.client.get(reverse('api-root:category-list'))
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 2)
        self.assertEqual(response_data.get('results')[0].get('category_name'), 'pakipsi')

    def test_exp_props_api(self):
        response = self.client.get(reverse('api-root:exs_props-list'))
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 2)
        self.assertEqual(response_data.get('results')[0].get('comment'), 'Test exp 1')

    def test_exp_props_api_detail_exists(self):
        response = self.client.get(reverse(
            'api-root:exs_props-detail',
            kwargs={'pk': 2}
        ))
        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('comment'), 'Test exp 2')

    def test_exp_props_api_detail_not_exists(self):
        response = self.client.get(reverse(
            'api-root:exs_props-detail',
            kwargs={'pk': 3}
        ))
        response_data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data.get('detail'), 'No ExchangeProposal matches the given query.')

    def test_exp_props_api_with_filter_on_title(self):
        data = {'ad_sender': 'TestAdminUser'}

        response = self.client.get(
            reverse('api-root:exs_props-list'),
            data=data
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('count'), 1)
        self.assertEqual(response_data.get('results')[0].get('comment'), 'Test exp 1')

    def test_exp_props_api_create(self):
        self.client.login(**self.user_2)
        data = {
            'ad_sender': self.ad_3.pk,
            'ad_receiver': self.ad_1.pk,
            'comment': 'A new test exp'
        }

        response = self.client.post(
            reverse('api-root:exs_props-list'),
            data=data,
            content_type='application/json'
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data.get('ad_sender'), 3)
        self.assertEqual(response_data.get('ad_receiver'), 1)
        self.assertEqual(response_data.get('comment'), 'A new test exp')
        self.assertEqual(response_data.get('status'), 'ожидает')

    def test_exp_props_api_update(self):
        self.client.login(**self.user_1)
        data = {
            'status': 'принята',
        }

        response = self.client.patch(
            reverse(
                'api-root:exs_props-detail',
                kwargs={'pk': 1}
            ),
            data=data,
            content_type='application/json'
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data.get('status'), 'принята')

    def test_exp_props_api_update_not_self(self):
        self.client.login(**self.admin)
        data = {
            'status': 'принята',
        }

        response = self.client.patch(
            reverse(
                'api-root:exs_props-detail',
                kwargs={'pk': 1}
            ),
            data=data,
            content_type='application/json'
        )

        response_data = response.json()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_data.get('detail'), 'У вас недостаточно прав для выполнения данного действия.')

