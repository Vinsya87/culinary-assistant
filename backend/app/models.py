from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

# class Unit(models.Model):
"""Модель на будущее чтобы создавать единицы измерения"""
#     title = models.CharField(
#         max_length=200,
#         default='г')

#     class Meta:
#         verbose_name = 'Единица измерения'
#         verbose_name_plural = 'Единицы измерения'

#     def __str__(self):
#         return self.title


class Tag(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=16, default='#FAFAFA')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=256, unique=True)
    measurement_unit = models.CharField(max_length=256, unique=False)
    # measurement_unit = models.ManyToManyField(
    #     Unit,
    #     blank=True,
    #     related_name='Units',
    #     verbose_name='Единицу измерения',
    #     help_text='Выберите единицу измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'Название рецепта',
        max_length=200,)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        default='Без имени',
        verbose_name='Автор',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )
    text = models.TextField(
        'Описание рецепта',
        help_text='Введите описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredientAmount',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='recipes_tag',
        verbose_name='Тег',
        help_text='Выберите Теги'
    )
    cooking_time = models.IntegerField(
        default=0,
        blank=True,
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredientAmount(models.Model):
    """Связующая модель для количества ингридиентов"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='igredients_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        validators=(
            MinValueValidator(
                1, message='Должно быть больше 1'),),
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user} {self.recipe}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name="unique_favorite")
        ]


class Subscription(models.Model):
    """Подписка на автора рецептов"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user} подписка на {self.author}'

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name="unique_followers")
        ]

    @property
    def recipe_count(self):
        recipes_count = Recipe.objects.filter(author=self.author).count
        return recipes_count


class Shopping(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopper',
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='purchases',
        verbose_name='Покупки',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user} {self.recipe}'

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name="unique_shopping")
        ]
