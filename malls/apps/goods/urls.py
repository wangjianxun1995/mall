from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^categories/(?P<category_id>\d+)/hotskus/$',views.HotSKUListAPIView.as_view(),name='hot'),

]