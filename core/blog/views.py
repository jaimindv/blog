from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets

# from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from base.permissions import (
    IsAPIKeyAuthenticated,
    IsRoleAuthorOrAdmin,
)

from .models import Blog
from .serializers import (
    BlogCreateUpdateSerializer,
    BlogDetailSerializer,
)


class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
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
                return Blog.objects.filter(author=user)
        return super().get_queryset()

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
            "list": BlogDetailSerializer,
            "create": BlogCreateUpdateSerializer,
            "update": BlogCreateUpdateSerializer,
            "partial_update": BlogCreateUpdateSerializer,
            "retrieve": BlogDetailSerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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
        instance = serializer.save()
        response_data = {
            "message": "Blog updated successfully.",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


# class CommentCreateView(generics.CreateAPIView):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
#     permission_classes = [permissions.AllowAny]

#     def perform_create(self, serializer):
#         blog = serializer.validated_data['blog']
#         if not blog.is_published:
#             raise serializers.ValidationError("Cannot comment on unpublished blogs.")
#         serializer.save(user=self.request.user)

# class CommentUpvoteDownvoteView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request, pk, action):
#         comment = Comment.objects.filter(pk=pk).first()
#         if not comment:
#             return Response({"error": "Comment not found."}, status=404)

#         if action == "upvote":
#             comment.upvotes += 1
#         elif action == "downvote":
#             comment.downvotes += 1
#         else:
#             return Response({"error": "Invalid action."}, status=400)

#         comment.save()
#         return Response({"message": f"Comment {action}d successfully."})

# class CommentDeleteView(generics.DestroyAPIView):
#     queryset = Comment.objects.all()
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return self.queryset.filter(blog__author=self.request.user)
