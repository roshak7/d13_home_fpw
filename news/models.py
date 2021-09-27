from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
# Comments
from django.contrib.contenttypes.fields import GenericRelation
from comment.models import Comment

class Author(models.Model):
    name = models.CharField(max_length=255, default='unnamed')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.name}'

    def update_rating(self):
        query_rating_post = Post.objects.filter(author=self, type="AR").values("rating")
        query_rating_comment = Comment.objects.filter(user=self.user).values("rating")
        query_rating_article = Comment.objects.filter(post__author=self, post__type="AR").values("rating")
        rating_article = 0
        rating_comment = 0
        rating_post = 0
        for qrp in query_rating_post:
            for key, value in qrp.items():
                rating_post += value*3

        for qrc in query_rating_comment:
            for key, value in qrc.items():
                rating_comment += value

        for qra in query_rating_article:
            for key, value in qra.items():
                rating_article += value

        self.rating = rating_post+rating_comment+rating_article
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, through='UserCategory')

    def __str__(self):
        return f'{self.name}'

class Post(models.Model):
    news = 'NS'
    article = 'AR'

    TYPE = [
        (news, 'Новость'),
        (article, 'Статья')
    ]
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=TYPE, default=news)
    date_posted = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    # the field name should be comments
    comments = GenericRelation(Comment)

    @property
    def in_category(self):
        list_of_category = [category.name for category in self.category.all()]
        return list_of_category

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:125]+'...'

    def get_absolute_url(self): # добавим абсолютный путь чтобы после создания нас перебрасывало на страницу с новостью
        return f'/news/{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'news-{self.pk}') # затем удаляем его из кэша, чтобы сбросить его


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

# class Comment(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     text = models.TextField()
#     date_posted = models.DateTimeField(auto_now_add=True)
#     rating = models.IntegerField(default=0)
#
#     def like(self):
#         self.rating += 1
#         self.save()
#
#     def dislike(self):
#         self.rating -= 1
#         self.save()
