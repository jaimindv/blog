from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BlogViewSet, CommentViewSet

router = DefaultRouter()
router.register("", BlogViewSet, basename="blogs")
router.register("comments/", CommentViewSet, basename="comments")

urlpatterns = [
    path("", include(router.urls)),
]
