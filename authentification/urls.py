from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register('users', views.UserViewSet, basename='users')
urlpatterns = [
    path('register', views.ResgisterAPIView.as_view(), name='register'),
    path('login', views.LoginAPIView.as_view(), name='login'),
    path('user', views.AuthUserAPIView.as_view(), name='user'),
    path('email_sign', views.EmailSign.as_view(), name='email_sign'),
    path('email_code', views.CodeVerification.as_view(), name='email_code'),
    path('update-access-date', views.AccessDateAPIView.as_view(), 
         name='update-access-date'),
]
urlpatterns += router.urls
