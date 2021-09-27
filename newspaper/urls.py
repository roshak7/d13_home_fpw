from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('comment/', include('comment.urls')),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('news/', include('news.urls')),  # делаем так, чтобы все адреса из нашего приложения (news/urls.py) сами автоматически подключались когда мы их добавим.
    path('', TemplateView.as_view(template_name='flatpages/home.html'), name='home'),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
]