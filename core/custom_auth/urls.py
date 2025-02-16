from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AppUserViewset, LoginView, LogoutView

router = DefaultRouter()

router.register("user", AppUserViewset, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
