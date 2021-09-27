from django.contrib import admin
from .models import Category, Post, Author, PostCategory

@admin.action(description='Обнулить рейтинги')
def nullfy_ratings(modeladmin, request, queryset): # все аргументы уже должны быть вам знакомы, самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    queryset.update(rating=0)

class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1


class NewsAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    inlines = (PostCategoryInline,)
    list_display = ['pk', 'type', 'title', 'author', 'in_category', 'date_posted', 'rating']
    list_display_links = ('pk', 'title',)
    list_filter = ('type', 'title', 'author', 'date_posted') # добавляем примитивные фильтры в нашу админку
    search_fields = ('type', 'title') # тут всё очень похоже на фильтры из запросов в базу
    actions = [nullfy_ratings]

admin.site.register(Category)
# admin.site.register(Comment)
admin.site.register(Author)
admin.site.register(Post, NewsAdmin)
