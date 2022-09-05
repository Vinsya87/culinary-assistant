from itertools import chain

from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredientAmount,
                     Shopping, Subscription, Tag)


class RecipeAmountAdmin(admin.TabularInline):
    model = RecipeIngredientAmount
    extra = 1
    min_num = 1


class RecipesAdmin(admin.ModelAdmin):
    def favorite_recipe(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    favorite_recipe.short_description = 'Количество добавлений в избранное'

    def ingredient_name(self, obj):
        a = obj.ingredients.values_list('name', 'measurement_unit')
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
      'pub_date', 'favorite_recipe')
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('author',)
    # filter_horizontal = ['tags']
    inlines = (RecipeAmountAdmin,)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    search_fields = ('name',)


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(Tag, TagsAdmin)
admin.site.register(Favorite)
admin.site.register(Subscription)
admin.site.register(Shopping)
