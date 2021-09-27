from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver  # импортируем нужный декоратор
from .models import Post
import datetime
from django.shortcuts import redirect
from .tasks import email_notifying

@receiver(pre_save, sender=Post)
def pre_save_handler(sender, instance, *args, **kwargs):
    start_date = datetime.datetime.today().date()
    end_date = start_date+datetime.timedelta(days=1)
    print(instance.author)
    posts_quantity = Post.objects.filter(author=instance.author, date_posted__range=(start_date, end_date))
    print(len(posts_quantity))
    if len(posts_quantity) > 3:
        redirect("too_many_posts.html")


# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(post_save, sender=Post)
def notify_users_news(sender, instance, created, **kwargs):
    if created:
        list_of_subscribers = []
        for c in instance.category.all():
            for usr in c.subscribers.all():
                list_of_subscribers.append(usr.pk)

        for usr_pk in list_of_subscribers:
            email_notifying.apply_async([instance.id, created, usr_pk], countdown=5)
