from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

urlpatterns = [
    path('read-name-plate', views.ReadNamePlateAPIView.as_view(),
         name='read-name-plate'),
]
urlpatterns += router.urls
