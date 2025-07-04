from rest_framework.routers import DefaultRouter
from django.urls import path, include

from ads.api.views import AdViewSet, ExchangeProposalViewSet as ExsProps, CategoryViewSet



app_name = 'api-root'


router = DefaultRouter()

router.register(r'ads', AdViewSet, basename='ads')
router.register(r'exs_props', ExsProps, basename='exs_props')
router.register(r'category', CategoryViewSet, basename='category')


urlpatterns = [
    path('', include(router.urls)),
]