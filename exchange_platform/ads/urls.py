from django.urls import path

from .views import (
    IndexView,
    DetailAdView,
    CreateAdView,
    UpdateAdView,
    DeleteAdView,
    CreateExcPropsView,
    ExcPropsView,
    DetailExcPropView,
    UpdateExcPropsView
)

app_name = 'ads'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('ad/<int:pk>', DetailAdView.as_view(), name='detail_ad'),
    path('create_ad/', CreateAdView.as_view(), name='create_ad'),
    path('update_ad/<int:pk>', UpdateAdView.as_view(), name='update_ad'),
    path('delete_ad/<int:pk>', DeleteAdView.as_view(), name='delete_ad'),
    path('exc_props/<int:pk>', CreateExcPropsView.as_view(), name='exc_props'),
    path('exc_props_list/', ExcPropsView.as_view(), name='exc_props_list'),
    path('detail_exc_props/<int:pk>', DetailExcPropView.as_view(), name='detail_exc_props'),
    path('update_exc_props/<int:pk>', UpdateExcPropsView.as_view(), name='update_exc_props'),
]
