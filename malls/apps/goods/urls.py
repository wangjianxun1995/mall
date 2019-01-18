from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^categories/(?P<category_id>\d+)/hotskus/$',views.HotSKUListAPIView.as_view(),name='hot'),

    url(r'^categories/(?P<category_id>\d+)/skus/$',views.SKUListView.as_view(),name='list'),

]

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls