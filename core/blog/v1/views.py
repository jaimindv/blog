from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action

# from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from base.permissions import IsAPIKeyAuthenticated, IsOwnerOrAdmin, IsRoleAuthorOrAdmin
from core.blog.models import Blog, Comment

from .serializers import (
    BlogCreateUpdateSerializer,
    BlogDetailSerializer,
    BlogListSerializer,
    CommentCreateUpdateSerializer,
    CommentSerializer,
)


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by("id")
    serializer_class = BlogDetailSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["author", "category", "tags", "is_published"]
    ordering_fields = ["id", "title"]
    search_fields = [
        "title",
        "content",
        "author__first_name",
        "author__email",
        "category__name",
        "tags__name",
    ]

    def get_queryset(self):
        if self.action in ["partial_update", "update", "destroy"]:
            user = self.request.user
            if user.role != "Admin" or not user.is_staff:
                return Blog.objects.filter(author=user).order_by("id")

        # Cache the queryset for better performance
        cache_key = "blog_list"
        cached_data = cache.get(cache_key)

        # Return cached data if any
        if cached_data:
            return cached_data

        queryset = super().get_queryset()
        # set cache data
        cache.set(cache_key, queryset)
        return queryset

    def get_permissions(self):
        # Only Author/Admins allowed to create/update/delete blogs
        if self.action in ["create", "update", "partial_update", "delete"]:
            self.permission_classes = [
                IsAPIKeyAuthenticated,
                IsAuthenticated,
                IsRoleAuthorOrAdmin,
            ]
        return super().get_permissions()

    def get_serializer_class(self):
        actions = {
            "list": BlogListSerializer,
            "create": BlogCreateUpdateSerializer,
            "update": BlogCreateUpdateSerializer,
            "partial_update": BlogCreateUpdateSerializer,
            "retrieve": BlogDetailSerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        blog_id = kwargs.get("pk")
        cache_key = f"blog_{blog_id}"
        cached_data = cache.get(cache_key)

        # Return cached data if any
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # set cache data
        cache.set(cache_key, serializer.data)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Clear cache as a new blog is added
        cache.delete("blog_list")

        response_data = {
            "message": "Blog created successfully.",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Clear cache
        cache.delete(f"blog_{instance.id}")
        cache.delete("blog_list")

        response_data = {
            "message": "Blog updated successfully.",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        blog_id = kwargs.get("pk")
        response = super().destroy(request, *args, **kwargs)

        # Clear cache
        cache.delete(f"blog_{blog_id}")
        cache.delete("blog_list")

        return response


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_serializer_class(self):
        actions = {
            "list": CommentSerializer,
            "create": CommentCreateUpdateSerializer,
            "update": CommentCreateUpdateSerializer,
            "partial_update": CommentSerializer,
            "retrieve": CommentSerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def get_permissions(self):
        # Only Author/Admins allowed to create/update/delete blogs
        if self.action in ["update", "partial_update", "delete"]:
            self.permission_classes = [
                IsAPIKeyAuthenticated,
                IsAuthenticated,
                IsOwnerOrAdmin,
            ]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Clear cache as a new comment is added
        blog_id = serializer.data.get("blog")
        cache.delete("blog_list")
        cache.delete(f"blog_{blog_id}")

        response_data = {
            "message": "Comment created successfully.",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Clear cache
        blog_id = serializer.data.get("blog")
        cache.delete("blog_list")
        cache.delete(f"blog_{blog_id}")

        response_data = {
            "message": "Comment updated successfully.",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="upvote")
    def upvote(self, request, pk=None):
        comment = self.get_object()
        comment.upvote(request.user)

        # Clear cache
        cache.delete("blog_list")
        cache.delete(f"blog_{comment.blog.id}")

        return Response({"message": "Comment upvoted."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="remove-upvote")
    def remove_upvote(self, request, pk=None):
        comment = self.get_object()
        comment.remove_upvote(request.user)

        # Clear cache
        cache.delete("blog_list")
        cache.delete(f"blog_{comment.blog.id}")

        return Response(
            {"message": "Comment upvote removed."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="downvote")
    def downvote(self, request, pk=None):
        comment = self.get_object()
        comment.downvote(request.user)

        # Clear cache
        cache.delete("blog_list")
        cache.delete(f"blog_{comment.blog.id}")

        return Response({"message": "Comment downvoted."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="remove-downvote")
    def remove_downvote(self, request, pk=None):
        comment = self.get_object()
        comment.remove_downvote(request.user)

        # Clear cache
        cache.delete("blog_list")
        cache.delete(f"blog_{comment.blog.id}")

        return Response(
            {"message": "Comment downvote removed."}, status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        comment_instance = self.get_object()
        if (
            request.user.role == "Admin"
            or comment_instance.user == request.user
            or comment_instance.blog.user == request.user
        ):
            comment_instance.delete()
            response_data = {
                "message": "Comment deleted successfully.",
            }

            # Clear cache
            cache.delete(f"blog_{comment_instance.blog.id}")
            cache.delete("blog_list")

            return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "You do not have permission to delete this comment"},
            status=status.HTTP_403_FORBIDDEN,
        )
