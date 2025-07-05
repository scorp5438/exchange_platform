from django.urls import path

from .views import IndexView, DetailAdView

app_name = 'ads'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('ad/<int:pk>', DetailAdView.as_view(), name='detail_ad'),
]
