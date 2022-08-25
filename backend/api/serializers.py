from app.models import (Favorite, Ingredient, Recipe, RecipeIngredientAmount,
                        Shopping, Subscription, Tag)
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'amount')


class IngredientListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    name = serializers.CharField()
    slug = serializers.CharField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class TagsCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Tag
        fields = ('id',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author',
                  'tags', 'ingredients', 'text', 'image',
                  'cooking_time'
                  )

    def validate(self, data):
        ingredients = data['ingredients']
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не уникальны!'
                })
            ingredients_list.append(ingredient_id)
        tags = data['tags']
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Тэги не уникальны!'
                })
            tags_list.append(tag)

        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time':
                'Проверьте время приготовления рецепта! (меньше 1)'
            })
        return data

    def create_ingredients(self, ingredients, recipe):
        ingredients_result = []
        """Метод для добавления ингредиентов"""
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(id=ingredient['id'])
            obj = RecipeIngredientAmount(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient['amount']
            )
            ingredients_result.append(obj)
        RecipeIngredientAmount.objects.bulk_create(ingredients_result)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        tags = self.initial_data.get('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, value):
        serializer = RecipeSerializer(value, context=self.context)
        return serializer.data

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.get(id=instance.id)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return super().update(instance, validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientSerializer(
        read_only=True, many=True, source='recipe_ingredients')
    tags = TagSerializer(many=True,)

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Shopping.objects.filter(
            user=request.user, recipe=obj).exists()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError('Нельзя использовать логин me')
        return data

    class Meta:
        fields = ('username', 'email')


class CreateUserSerializer(serializers.ModelSerializer):
    last_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class FavoriteSerializer(serializers.ModelSerializer):
    """Рецепт в избранное"""
    image = Base64ImageField()
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    pass


class RecipesSer(serializers.ModelSerializer):
    image = Base64ImageField()
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsUserSerializer(serializers.ModelSerializer):
    """Получения списка авторов и их рецептов на кого подписан пользователь"""
    email = serializers.EmailField(read_only=True, source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipe_count')
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
            )

    def get_recipes(self, obj):
        recipe = obj.author.recipes_author.all()
        return RecipesSer(recipe, many=True).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Subscription.objects.filter(
            user=request.user, author=obj.author).exists()


class SubscriptionsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'
