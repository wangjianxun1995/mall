from django.conf.urls import url

from users.views import UserEMailVerificationAPIView
from . import views
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [

    url(r'^usernames/(?P<username>\w{5,20}/count/$)',views.RegisterUsernameCountAPIView.as_view()),
    # url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameAPIView.as_view(),name='usernamecount'),
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$',views.RegisterPhoneCountAPIView.as_view()),
    url(r'^$',views.RegiserUserAPIView.as_view()),
    url(r'^auths',obtain_jwt_token),
    url(r'infos/$',views.UserCenterInfoAPIView.as_view()),
    url(r'emails/$',views.UserEmaileInfoAPIView.as_view()),
    url(r'^emails/verification/$',UserEMailVerificationAPIView.as_view()),
    # url(r'^addresses/$',views.UserAddressAPIView.as_view()),
    url(r'^browerhistories/$',views.UserBrowsingHistoryView.as_view(),name='history'),
]
from .views import UserAddressAPIView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'addresses',UserAddressAPIView,base_name='address')
urlpatterns += router.urls