from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .pagination import InfiniteScrollPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import AdSerializer, ExchangeProposalSerializer, CategorySerializer
from ..models import Ad, ExchangeProposal, Category
from .filters import ExchangeProposalFilter

class AdViewSet(ModelViewSet):
    queryset = Ad.objects.select_related('category', 'user').all()
    serializer_class = AdSerializer
    pagination_class = InfiniteScrollPagination
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = ['title', 'description', 'condition', 'category']
    search_fields = ['title', 'description', 'category__category_name', ]
    ordering_fields = ['pk', 'title', 'type', 'condition', 'created_at', ]
    ordering = ['pk']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExchangeProposalViewSet(ModelViewSet):
    queryset = ExchangeProposal.objects.select_related('ad_sender__user', 'ad_receiver__user').all()
    serializer_class = ExchangeProposalSerializer
    pagination_class = InfiniteScrollPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ExchangeProposalFilter
    ordering = ['pk']


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
