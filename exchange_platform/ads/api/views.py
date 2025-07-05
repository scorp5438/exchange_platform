from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from .pagination import InfiniteScrollPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import AdSerializer, ExchangeProposalSerializer, CategorySerializer
from ..models import Ad, ExchangeProposal, Category


class AdViewSet(ModelViewSet):
    queryset = Ad.objects.select_related('category', 'user').all()
    serializer_class = AdSerializer
    pagination_class = InfiniteScrollPagination
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['title', 'description', 'condition', 'category']
    search_fields = [
        'title',
        'description',
        'category__category_name',
    ]
    ordering_fields = ['pk', 'title', 'type', 'condition', 'created_at', ]
    ordering = ['-pk']

class ExchangeProposalViewSet(ModelViewSet):
    queryset = ExchangeProposal.objects.select_related('ad_sender', 'ad_receiver').all()
    serializer_class = ExchangeProposalSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
