from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse

from .models import Ad, Category, ExchangeProposal


class BaseTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = {
            'username': 'TestAdminUser',
            'password': 'qwerty',
            'is_staff': True,
            'is_superuser': True
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

        cls.exp_props_1 = ExchangeProposal.objects.create(
            ad_sender=cls.ad_1,
            ad_receiver=cls.ad_2,
            comment='Test exp 1',
        )
        cls.exp_props_2 = ExchangeProposal.objects.create(
            ad_sender=cls.ad_3,
            ad_receiver=cls.ad_4,
            comment='Test exp 2',
        )


class AdsAppApiViewTestCase(BaseTest):


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


class IndexViewTest(BaseTest):
    def test_excludes_ads_with_accepted_proposals(self):
        ExchangeProposal.objects.filter(ad_sender=self.ad_1).update(status='принята')
        response = self.client.get(reverse('ads:index'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.ad_1.title)
        self.assertNotContains(response, self.ad_2.title)
        self.assertContains(response, self.ad_3.title)
        self.assertContains(response, self.ad_4.title)
        self.assertEqual(len(response.context['object_list']), 2)

    def test_show_ads_when_no_accepted_proposals(self):
        response = self.client.get(reverse('ads:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad_1.title)
        self.assertContains(response, self.ad_2.title)
        self.assertContains(response, self.ad_3.title)
        self.assertContains(response, self.ad_4.title)
        self.assertEqual(len(response.context['object_list']), 4)

    def test_category_filter(self):
        response = self.client.get(
            reverse('ads:index') + f'?category={self.category_1.id}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad_1.title)
        self.assertContains(response, self.ad_2.title)
        self.assertNotContains(response, self.ad_3.title)
        self.assertNotContains(response, self.ad_4.title)
        self.assertEqual(response.context['current_category'], str(self.category_1.id))

    def test_condition_filter(self):
        ExchangeProposal.objects.all().update(status='ожидает')

        url = reverse('ads:index') + '?condition=Новый'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad_1.title)
        self.assertContains(response, self.ad_2.title)
        self.assertNotContains(response, self.ad_3.title)
        self.assertNotContains(response, self.ad_4.title)
        self.assertEqual(response.context['current_condition'], 'Новый')

    def test_template_and_status_code(self):
        response = self.client.get(reverse('ads:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/index.html')

    def test_context_data(self):
        response = self.client.get(reverse('ads:index'))

        self.assertIn('categories', response.context)
        self.assertEqual(len(response.context['categories']), 2)
        self.assertIn('conditions', response.context)
        self.assertEqual(len(response.context['conditions']), len(Ad.CONDITION))
        self.assertEqual(response.context['search_query'], '')
        self.assertEqual(response.context['current_category'], '')
        self.assertEqual(response.context['current_condition'], '')


class DetailAdViewTest(BaseTest):
    def test_detail_view_returns_correct_ad(self):
        # Проверяем отображение каждого объявления
        for ad in [self.ad_1, self.ad_3]:
            url = reverse('ads:detail_ad', kwargs={'pk': ad.pk})
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'ads/detail.html')
            self.assertEqual(response.context['object'], ad)
            self.assertContains(response, ad.title)
            self.assertContains(response, ad.description)
            self.assertContains(response, ad.category.category_name)
            self.assertContains(response, ad.user.username)

    def test_detail_view_returns_404_for_invalid_pk(self):
        invalid_url = reverse('ads:detail_ad', kwargs={'pk': 99})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


class CreateAdViewTest(BaseTest):
    def setUp(self):
        self.client.login(**self.user_1)

    def test_create_ad_view_uses_correct_template(self):
        response = self.client.get(reverse('ads:create_ad'))
        self.assertTemplateUsed(response, 'ads/create_ad.html')

    def test_create_ad_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('ads:create_ad'))
        self.assertEqual(response.status_code, 302)

    def test_create_ad_success(self):
        data = {
            'title': 'New ad',
            'description': 'A new description',
            'category': self.category_1.id,
            'condition': 'Новый',
        }

        response = self.client.post(
            reverse('ads:create_ad'),
            data=data,
            follow=True
        )

        self.assertRedirects(response, reverse('ads:index'))

        new_ad = Ad.objects.get(title='New ad')
        self.assertEqual(new_ad.user, self.test_user_1)
        self.assertEqual(new_ad.description, 'A new description')
        self.assertEqual(new_ad.category, self.category_1)
        self.assertEqual(new_ad.condition, 'Новый')

    def test_create_ad_invalid_title(self):
        form_data = {
            'title': '',
            'description': 'Невалидное объявление',
            'category': self.category_1.id,
            'condition': 'Новый',
        }

        response = self.client.post(reverse('ads:create_ad'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Обязательное поле.')

    def test_create_ad_invalid_category(self):
        # Сначала создаем валидные данные
        valid_data = {
            'title': 'A new title for test',
            'description': 'description for create',
            'category': self.category_1.id,
            'condition': 'Новый',
        }

        invalid_data = valid_data.copy()
        invalid_data['category'] = 9999

        response = self.client.post(reverse('ads:create_ad'), data=invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'category',
                             'Выберите корректный вариант. Вашего варианта нет среди допустимых значений.')


class UpdateAdViewTest(BaseTest):
    def setUp(self):
        self.client.login(**self.user_1)

    def test_update_view_owner_access(self):
        response = self.client.get(reverse('ads:update_ad', kwargs={'pk': self.ad_2.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/update_ad.html')

    def test_update_view_non_owner_access(self):
        url = reverse('ads:update_ad', kwargs={'pk': self.ad_1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_successful_update_redirect(self):
        form_data = {
            'title': 'Update title',
            'description': 'New description',
            'category': self.category_1.id,
            'condition': 'б/у',
        }
        response = self.client.post(
            reverse(
                'ads:update_ad',
                kwargs={'pk': self.ad_2.pk}
            ),
            data=form_data
        )
        self.assertRedirects(response, reverse('ads:detail_ad', kwargs={'pk': self.ad_2.pk}))
        self.ad_2.refresh_from_db()
        self.assertEqual(self.ad_2.title, 'Update title')


class DeleteAdViewTest(BaseTest):
    def setUp(self):
        # Создаем дополнительное объявление для тестов
        self.ad_to_delete = Ad.objects.create(
            user=self.test_user_1,
            title='Deleted ad',
            description='Test deleted',
            category=self.category_1,
            condition='Новый'
        )

    def test_admin_can_delete_any_ad(self):
        self.client.login(**self.admin)
        delete_url = reverse('ads:delete_ad', kwargs={'pk': self.ad_to_delete.pk})

        response = self.client.post(reverse(
            'ads:delete_ad',
            kwargs={'pk': self.ad_to_delete.pk}
        ))

        self.assertRedirects(response, reverse('ads:index'))
        self.assertFalse(Ad.objects.filter(pk=self.ad_to_delete.pk).exists())

    def test_other_user_cannot_delete_ad(self):
        self.client.login(**self.user_2)

        response = self.client.post(reverse(
            'ads:delete_ad',
            kwargs={'pk': self.ad_to_delete.pk}
        ))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Ad.objects.filter(pk=self.ad_to_delete.pk).exists())

    def test_anonymous_user_cannot_delete_ad(self):
        response = self.client.post(reverse(
            'ads:delete_ad',
            kwargs={'pk': self.ad_to_delete.pk}
        ))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
        self.assertTrue(Ad.objects.filter(pk=self.ad_to_delete.pk).exists())


class ExcPropsViewTest(BaseTest):
    def setUp(self):
        self.client.login(**self.user_1)

    def test_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('ads:exc_props_list'))
        self.assertEqual(response.status_code, 302)

    def test_show_only_user_related_proposals(self):
        response = self.client.get(reverse('ads:exc_props_list'))

        self.assertEqual(len(response.context['object_list']), 1)
        self.assertIn(self.exp_props_1, response.context['object_list'])
        self.assertNotIn(self.exp_props_2, response.context['object_list'])

    def test_status_filter(self):
        self.client.logout()
        self.client.login(**self.user_2)
        ExchangeProposal.objects.filter(ad_sender=self.ad_3).update(status='принята')
        response = self.client.get(reverse('ads:exc_props_list') + '?status=принята')

        self.assertEqual(len(response.context['object_list']), 1)
        self.assertIn(self.exp_props_2, response.context['object_list'])
        self.assertEqual(response.context['current_status'], 'принята')

    def test_type_filter_sent(self):
        self.client.logout()
        self.client.login(**self.user_2)
        response = self.client.get(reverse('ads:exc_props_list') + '?type=sent')

        self.assertEqual(len(response.context['object_list']), 1)
        self.assertIn(self.exp_props_2, response.context['object_list'])


class CreateExcPropsViewTest(BaseTest):
    def setUp(self):
        self.client.login(**self.user_1)

    def test_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('ads:exc_props', kwargs={'pk': self.ad_2.pk}))
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_successful_proposal_creation(self):
        form_data = {
            'comment': 'Test proposal comment',
            'ad_sender': self.ad_2.pk
        }

        response = self.client.post(
            reverse('ads:exc_props', kwargs={'pk': self.ad_1.pk}),
            data=form_data
        )

        self.assertRedirects(response, reverse('ads:detail_ad', kwargs={'pk': self.ad_1.pk}))

        proposal = ExchangeProposal.objects.last()
        self.assertEqual(proposal.ad_sender, self.ad_2)
        self.assertEqual(proposal.ad_receiver, self.ad_1)
        self.assertEqual(proposal.comment, 'Test proposal comment')


class DetailExcPropViewTest(BaseTest):
    def setUp(self):
        self.exp_props_3 = ExchangeProposal.objects.create(
            ad_sender=self.ad_1,
            ad_receiver=self.ad_3,
            comment="Test proposal",
            status='ожидает'
        )
        self.client.login(**self.user_1)

    def test_contains_proposal_in_context(self):
        response = self.client.get(reverse(
            'ads:detail_exc_props',
            kwargs={'pk': self.exp_props_3.pk}
        ))
        self.assertEqual(response.context['object'], self.exp_props_3)
        self.assertEqual(response.context['exchangeproposal'], self.exp_props_3)

    def test_contains_related_ads_in_context(self):
        self.client.login(**self.user_1)
        response = self.client.get(reverse(
            'ads:detail_exc_props',
            kwargs={'pk': self.exp_props_2.pk}
        ))

        self.assertEqual(response.context['object'].ad_sender, self.ad_3)
        self.assertEqual(response.context['object'].ad_receiver, self.ad_4)
        self.assertEqual(response.context['object'].ad_sender.user, self.test_user_2)
        self.assertEqual(response.context['object'].ad_receiver.user, self.admin_user)

    def test_returns_404_for_invalid_pk(self):
        self.client.login(username='TestUse_1', password='qwerty')
        invalid_url = reverse('ads:detail_exc_props', kwargs={'pk': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


class UpdateExcPropsViewTest(BaseTest):

    def test_sender_can_update_comment(self):
        self.client.login(**self.admin)
        url = reverse('ads:update_exc_props', kwargs={'pk': self.exp_props_1.pk})

        form_data = {
            'comment': 'Updated comment by sender',
            'ad_sender': self.ad_1.pk  # ad_1 принадлежит admin_user
        }

        response = self.client.post(url, data=form_data)

        self.assertRedirects(response, reverse('ads:detail_exc_props', kwargs={'pk': self.exp_props_1.pk}))
        self.exp_props_1.refresh_from_db()
        self.assertEqual(self.exp_props_1.comment, 'Updated comment by sender')
        self.assertEqual(self.exp_props_1.ad_sender, self.ad_1)

    def test_receiver_can_update_status(self):
        self.client.login(**self.user_1)
        url = reverse('ads:update_exc_props', kwargs={'pk': self.exp_props_1.pk})

        form_data = {
            'status': 'принята'
        }

        response = self.client.post(url, data=form_data)

        self.assertRedirects(response, reverse('ads:detail_exc_props', kwargs={'pk': self.exp_props_1.pk}))
        self.exp_props_1.refresh_from_db()
        self.assertEqual(self.exp_props_1.status, 'принята')

    def test_other_user_cannot_update(self):
        self.client.login(**self.user_2)

        response = self.client.get(reverse(
                'ads:update_exc_props',
                kwargs={'pk': self.exp_props_1.pk}
            ))

    def test_invalid_status_update(self):
        self.client.login(**self.user_1)
        url = reverse('ads:update_exc_props', kwargs={'pk': self.exp_props_1.pk})

        form_data = {
            'status': 'несуществующий_статус'
        }

        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Выберите корректный вариант.',
            response.context['form'].errors['status'][0]
        )