# from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView  # импортируем класс, который говорит нам о том, что в этом представлении мы будем выводить список объектов из БД
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Post, Category
from .filters import NewsFilter
from .forms import PostForm # импортируем нашу форму

from django.db.models.signals import post_save, pre_save
from .signals import notify_users_news, pre_save_handler

from django.core.cache import cache

pre_save.connect(pre_save_handler, sender=Post)
post_save.connect(notify_users_news, sender=Post)

class FilteredListView(ListView):
    filterset_class = None

    def get_queryset(self):
        # Get the queryset however you usually would.  For example:
        queryset = super().get_queryset()
        # Then use the query parameters and the queryset to
        # instantiate a filterset and save it as an attribute
        # on the view instance for later.
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        # Return the filtered queryset
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the filterset to the template - it provides the form.
        context['filterset'] = self.filterset
        return context


class SearchNewsList(FilteredListView):
    filterset_class = NewsFilter
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'search.html'  # указываем имя шаблона, в котором будет лежать html, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'news'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через html-шаблон
    queryset = Post.objects.order_by('-date_posted')
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['post_count'] = len(Post.objects.all())
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())   # вписываем наш фильтр в контекст
        return context

class NewsList(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news.html'  # указываем имя шаблона, в котором будет лежать html, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'news'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через html-шаблон
    queryset = Post.objects.order_by('-date_posted')
    paginate_by = 3
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_count'] = len(Post.objects.all())
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST запроса

        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не накосячил то сохраняем новый товар
            form.save()
        return super().get(request, *args, **kwargs)

class NewsDetail(DetailView):
    model = Post  # модель всё та же, но мы хотим получать детали конкретно отдельного товара
    template_name = 'news_detail.html'  # название шаблона будет product.html
    context_object_name = 'news_detail'  # название объекта. в нём будет
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'news-{self.kwargs["pk"]}',
                        None)  # кэш очень похож на словарь, и метод get действует также. Он забирает значение по ключу, если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object()
            cache.set(f'news-{self.kwargs["pk"]}', obj)

        return obj


class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post  # модель всё та же, но мы хотим получать детали конкретно отдельного товара
    template_name = 'news_create.html'
    context_object_name = 'news_detail'  # название объекта. в нём будет
    form_class = PostForm
    permission_required = ('news.add_post',)

class NewsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post  # модель всё та же, но мы хотим получать детали конкретно отдельного товара
    template_name = 'news_create.html'
    context_object_name = 'news_detail'  # название объекта. в нём будет
    form_class = PostForm
    permission_required = ('news.change_post',)

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

# дженерик для удаления товара
class NewsDeleteView(PermissionRequiredMixin, DeleteView):
    model = Post  # модель всё та же, но мы хотим получать детали конкретно отдельного товара
    template_name = 'news_delete.html'
    context_object_name = 'post'  # название объекта. в нём будет
    queryset = Post.objects.all()
    success_url = '/news/'
    permission_required = ('news.delete_post',)

class CategoryList(ListView):
    model = Category  # указываем модель, объекты которой мы будем выводить
    template_name = 'category.html'  # указываем имя шаблона, в котором будет лежать html, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'categorys'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через html-шаблон
    paginate_by = 5


@login_required
def subscribe_me(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    if category not in user.category_set.all():
        category.subscribers.add(user)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))

@login_required
def unsubscribe_me(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    if category in user.category_set.all():
        category.subscribers.remove(user)
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))

def update_rating_up(request, pk):
    post = Post.objects.get(id=pk)
    post.like()
    return redirect(request.META.get('HTTP_REFERER'))

def update_rating_down(request, pk):
    post = Post.objects.get(id=pk)
    post.dislike()
    return redirect(request.META.get('HTTP_REFERER'))
