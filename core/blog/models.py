from django.db import models

from core.custom_auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(max_length=255)
    publication_date = models.DateField(null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs")
    content = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="blogs"
    )
    tags = models.ManyToManyField(Tag, related_name="blogs")
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self", null=True, on_delete=models.CASCADE, related_name="replies"
    )
    upvoted_by = models.ManyToManyField(User, related_name="upvoted_comments")
    downvoted_by = models.ManyToManyField(User, related_name="downvoted_comments")

    @property
    def upvote_count(self):
        return self.upvoted_by.count()

    @property
    def downvote_count(self):
        return self.downvoted_by.count()

    def upvote(self, user):
        if user in self.downvoted_by.all():
            self.downvoted_by.remove(user)
        self.upvoted_by.add(user)

    def downvote(self, user):
        if user in self.upvoted_by.all():
            self.upvoted_by.remove(user)
        self.downvoted_by.add(user)

    def remove_upvote(self, user):
        if user in self.upvoted_by.all():
            self.upvoted_by.remove(user)

    def remove_downvote(self, user):
        if user in self.downvoted_by.all():
            self.downvoted_by.remove(user)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.blog.title}"
