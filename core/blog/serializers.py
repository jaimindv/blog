from django.utils import timezone
from rest_framework import serializers

from core.custom_auth.models import User

from .models import Blog, Category, Comment, Tag


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "bio",
            "profile_pic",
        ]


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
        ]


class BlogCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "publication_date",
            "is_published",
            "author",
            "content",
            "category",
            "tags",
        ]
        extra_kwargs = {"author": {"required": False}}

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        validated_data.update({"author": user})
        is_published = validated_data.get("is_published", False)
        if is_published:
            validated_data.update({"publication_date": timezone.now().date()})
        blog_instance = super().create(validated_data)
        return blog_instance

    def update(self, instance, validated_data):
        is_published = validated_data.get("is_published", False)
        if is_published:
            validated_data.update({"publication_date": timezone.now().date()})
        blog_instance = super().update(instance, validated_data)
        return blog_instance


class BlogListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "publication_date",
            "is_published",
            "author",
            "content",
            "category",
            "tags",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            "id",
            "blog",
            "user",
            "text",
            "created_at",
            "parent",
            "upvoted_by",
            "downvoted_by",
            "upvote_count",
            "downvote_count",
        ]


class BlogDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "publication_date",
            "is_published",
            "author",
            "content",
            "category",
            "tags",
            "comments",
        ]
