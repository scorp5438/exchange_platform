from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from .serializers import AdSerializer, ExchangeProposalSerializer, CategorySerializer
from ..models import Ad, ExchangeProposal, Category
from .permissions import IsOwnerOrReadOnly

class AdViewSet(ModelViewSet):
    queryset = Ad.objects.select_related('category', 'user').all()
    serializer_class = AdSerializer
    permission_classes = [IsOwnerOrReadOnly]


class ExchangeProposalViewSet(ModelViewSet):
    queryset = ExchangeProposal.objects.select_related('ad_sender', 'ad_receiver').all()
    serializer_class = ExchangeProposalSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
