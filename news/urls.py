from django.urls import path
from .views import NewsList, NewsDetail, SearchNewsList, NewsCreateView, NewsUpdateView, NewsDeleteView, subscribe_me, unsubscribe_me, CategoryList, update_rating_up, update_rating_down# импортируем наше представление

urlpatterns = [
    # path — означает путь. В данном случае путь ко всем товарам у нас останется пустым, позже станет ясно почему
    path('', NewsList.as_view()),
    path('category/', CategoryList.as_view()),
    path('search/', SearchNewsList.as_view()),
    path('create/', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/update', NewsUpdateView.as_view(), name='news_update'),
    path('<int:pk>/delete', NewsDeleteView.as_view(), name='news_delete'),
    path('<int:pk>', NewsDetail.as_view(), name='news_detail'),  # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
    path('subscribe/<int:pk>', subscribe_me),
    path('unsubscribe/<int:pk>', unsubscribe_me),
    path('plusrating/<int:pk>', update_rating_up),
    path('minusrating/<int:pk>', update_rating_down),
    path('category/subscribe/<int:pk>', subscribe_me),
    path('category/unsubscribe/<int:pk>', unsubscribe_me),
]
