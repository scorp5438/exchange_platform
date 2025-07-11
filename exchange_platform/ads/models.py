from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill, ResizeToFit


class Ad(models.Model):
    CONDITION = [
        ('Новый', 'Новый'),
        ('б/у', 'б/у'),
    ]
    user = models.ForeignKey(
        to=User,
        on_delete=CASCADE,
        related_name='ads',
        related_query_name='ad',
    )
    title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        db_index=True,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        max_length=3000,
        blank=False,
        null=False,
        db_index=True,
        verbose_name='Описание товара'
    )
    image_url = ProcessedImageField(
        upload_to='images/',
        processors=[ResizeToFit(450, 340)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True,
        verbose_name='Изображение товара'
    )
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='ads'
    )
    condition = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        choices=CONDITION,
        db_index=True,
        verbose_name='Состояние товара'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания'
    )

    class Meta:
        ordering = ['pk']
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявление'

    def get_image_url(self):
        """Возвращает относительный URL изображения или None если изображения нет"""
        # return f'/media/{self.image_url.name}' if self.image_url else None
        return self.image_url.url if self.image_url else None

    def get_short_description(self):
        return f'{self.description[:25]}...'

    def __str__(self):
        return self.title


class ExchangeProposal(models.Model):
    STATUSES = [
        ('ожидает', 'ожидает'),
        ('принята', 'принята'),
        ('отклонена', 'отклонена'),
    ]
    ad_sender = models.ForeignKey(
        to=Ad,
        on_delete=CASCADE,
        related_name='sent_proposals',
        verbose_name='Отправитель'

    )
    ad_receiver = models.ForeignKey(
        to=Ad,
        on_delete=CASCADE,
        related_name='received_proposals',
        verbose_name='Получатель'
    )
    comment = models.TextField(
        max_length=3000,
        blank=False,
        null=False,
        db_index=True,
        verbose_name='Комментарий'
    )
    status = models.CharField(
        max_length=50,
        default='ожидает',
        choices=STATUSES,
        db_index=True,
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания'
    )

    class Meta:
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложение обмена'

    def __str__(self):
        return f'Предложение #{self.pk} ({self.status})'


class Category(models.Model):
    category_name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        db_index=True,
        verbose_name='Наименование категории'
    )

    class Meta:
        ordering = ['pk']
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категория'

    def __str__(self):
        return self.category_name
