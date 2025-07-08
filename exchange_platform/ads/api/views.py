from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from .pagination import InfiniteScrollPagination
from .permissions import IsOwnerOrReadOnly, IsSenderOrReadOnly
from .serializers import AdSerializer, ExchangeProposalSerializer, CategorySerializer
from ..models import Ad, ExchangeProposal, Category
from .filters import ExchangeProposalFilter

class AdViewSet(ModelViewSet):
    """
         ViewSet для работы с объявлениями (Ad).

         Предоставляет стандартные CRUD-операции для модели Ad с дополнительными возможностями:
         - Пагинация (бесконечная прокрутка)
         - Фильтрация, поиск и сортировка
         - Контроль доступа (только владелец может изменять/удалять)

         Фильтрация:
             Поддерживается фильтрация по:
             - title (точное совпадение или частичное без учета регистра)
             - description (точное совпадение или частичное без учета регистра)
             - condition (точное совпадение)
             - category (точное совпадение)

         Поиск:
             Поиск осуществляется по полям:
             - title
             - description
             - category__category_name (название категории)

         Сортировка:
             Доступна сортировка по полям:
             - pk (ID объявления)
             - title (заголовок)
             - type (тип объявления)
             - condition (состояние товара)
             - created_at (дата создания)
             По умолчанию сортировка по pk.

         Методы:
             perform_create(serializer): Автоматически устанавливает текущего пользователя
                                        как владельца создаваемого объявления.

         Примеры запросов:
             GET /ads/ - список всех объявлений
             GET /ads/?search=телефон - поиск объявлений с "телефон" в названии или описании
             GET /ads/?ordering=-created_at - объявления, отсортированные по дате (новые сначала)
             GET /ads/?condition=Новый - только новые товары
             POST /ads/ - создание нового объявления
             PATCH /ads/<id>/ - частичное обновление объявления
             DELETE /ads/<id>/ - удаление объявления
         """
    queryset = Ad.objects.select_related('category', 'user').all()
    serializer_class = AdSerializer
    pagination_class = InfiniteScrollPagination
    permission_classes = [IsOwnerOrReadOnly,]
    http_method_names = ['get', 'post', 'patch', 'delete']

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = {
        'title': ['exact', 'icontains'],
        'description': ['exact', 'icontains'],
        'condition': ['exact'],
        'category': ['exact'],
    }
    search_fields = ['title', 'description', 'category__category_name', ]
    ordering_fields = ['pk', 'title', 'type', 'condition', 'created_at', ]
    ordering = ['pk']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExchangeProposalViewSet(ModelViewSet):
    """
        ViewSet для работы с предложениями обмена (ExchangeProposal).

        Предоставляет стандартные CRUD-операции для модели ExchangeProposal с возможностями:
        - Пагинация (бесконечная прокрутка)
        - Фильтрация через специальный класс фильтров
        - Сортировка результатов
        - Контроль доступа (только отправитель может изменять/удалять предложение)

        Фильтрация:
            Реализована через специальный класс ExchangeProposalFilter, который должен поддерживать:
            - Фильтрацию по статусу предложения
            - Фильтрацию по отправителю/получателю объявления
            - Другие параметры фильтрации

        Сортировка:
            Доступна сортировка по стандартным полям модели.
            По умолчанию сортировка по pk (ID предложения).

        Статусы предложений:
            - ожидает (по умолчанию)
            - принята
            - отклонена

        Методы:
            perform_create(serializer): Автоматически устанавливает текущего пользователя
                                       как отправителя предложения при создании.

        Примеры запросов:
            GET /proposals/ - список всех предложений обмена
            GET /proposals/?status=принята - только принятые предложения
            GET /proposals/?ordering=-created_at - предложения, отсортированные по дате (новые сначала)
            POST /proposals/ - создание нового предложения обмена
            PATCH /proposals/<id>/ - обновление статуса или комментария предложения
            DELETE /proposals/<id>/ - удаление предложения
        """
    queryset = ExchangeProposal.objects.select_related('ad_sender__user', 'ad_receiver__user').all()
    serializer_class = ExchangeProposalSerializer
    pagination_class = InfiniteScrollPagination
    permission_classes = [IsSenderOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ExchangeProposalFilter
    ordering = ['pk']


class CategoryViewSet(ModelViewSet):
    """
        ViewSet для работы с категориями товаров (Category).

        Предоставляет стандартные CRUD-операции для модели Category:
        - Создание новых категорий
        - Просмотр списка категорий и деталей конкретной категории
        - Обновление существующих категорий
        - Удаление категорий

        Особенности:
            - Не использует пагинацию (все категории возвращаются одним списком)
            - Нет специальных разрешений (доступ определяется на уровне маршрутизации)
            - Разрешены все стандартные HTTP-методы (GET, POST, PUT, PATCH, DELETE)

        Поля модели:
            - category_name: Название категории (обязательное поле)
            - pk/id: Уникальный идентификатор категории

        Примеры запросов:
            GET /categories/ - список всех категорий
            GET /categories/<id>/ - получение конкретной категории
            POST /categories/ - создание новой категории
                Пример тела запроса: {"category_name": "Электроника"}
            PUT /categories/<id>/ - полное обновление категории
            PATCH /categories/<id>/ - частичное обновление категории
            DELETE /categories/<id>/ - удаление категории
        """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
