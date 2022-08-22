from itertools import chain

from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredientAmount,
                     Shopping, Subscription, Tag)


class RecipeAmountAdmin(admin.TabularInline):
    model = RecipeIngredientAmount
    extra = 1


class RecipesAdmin(admin.ModelAdmin):
    def ingredient_name(self, obj):
        a = obj.ingredients.values_list('name')
        return list(chain.from_iterable(a))
    ingredient_name.short_description = 'Ингредиент'

    def tag_name(self, obj):
        a = obj.tags.values_list('name')
        return list(chain.from_iterable(a))
    tag_name.short_description = 'Тег'

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
    list_display = (
      'pk', 'name',
      'author', 'text',
      'image', 'cooking_time',
      'tag_name', 'ingredient_name',
      'pub_date')
    search_fields = ('text', 'name', 'author',)
    list_filter = ('author',)
    filter_horizontal = ['tags']
    inlines = (RecipeAmountAdmin,)
    # Это свойство сработает для всех колонок: где пусто — там будет эта строка
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    empty_value_display = '-пусто-'
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(Subscription)
admin.site.register(Shopping)
