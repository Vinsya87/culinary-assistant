from api.permissions import OwnerOrAdmins
from api.serializers import (FavoriteSerializer, IngredientListSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             SubscriptionsUserSerializer, TagSerializer)
from app.models import (Favorite, Ingredient, Recipe, Shopping, Subscription,
                        Tag)
from app.servises import download_shopping
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from users.models import User

from .filter import IngredientSearchFilter, RecipeFilter


class CreateDeleteShopping(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    def create(self, request, *args, **kwargs):
        """Добавления рецепта
        в список покупок
        """
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('shop_id'))
        if Shopping.objects.filter(user=self.request.user,
                                   recipe=recipe).exists():
            raise ValidationError([
                'Нельзя добавить один и тот же рецепт в список покупок'])
        Shopping.objects.create(user=request.user, recipe=recipe)
        serializer = FavoriteSerializer()
        return Response(
            serializer.to_representation(instance=recipe),
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        """Удаление рецепта
        из списка покупок
        """
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('shop_id'))
        if Shopping.objects.filter(user=self.request.user,
                                   recipe=recipe).exists():
            Shopping.objects.filter(user=self.request.user,
                                    recipe=recipe).delete()
            return Response([
                    'Рецепт успешно удален из списка покупок'],
                    status=status.HTTP_204_NO_CONTENT)
        raise ValidationError([
                'Рецепта нет в списке покупок'])


class CreateDeleteFavorite(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    def create(self, request, *args, **kwargs):
        """Добавления рецепта
        в список избранного
        """
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        if Favorite.objects.filter(user=self.request.user,
                                   recipe=recipe).exists():
            raise ValidationError([
                'Нельзя подписаться на один и тот же рецепт дважды'])
        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = FavoriteSerializer()
        return Response(
            serializer.to_representation(instance=recipe),
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        """Удаление рецепта
        из списка избранного
        """
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        if Favorite.objects.filter(user=self.request.user,
                                   recipe=recipe).exists():
            Favorite.objects.filter(user=self.request.user,
                                    recipe=recipe).delete()
            return Response([
                    'Рецепт успешно удален из избранного'],
                    status=status.HTTP_204_NO_CONTENT)
        raise ValidationError([
                'Рецепта нет в избранном'])


class CreateDeleteSubscriptions(mixins.CreateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    def create(self, request, *args, **kwargs):
        """Добавления рецепта
        в список избранного
        """
        author = get_object_or_404(
            User, id=self.kwargs.get('follow_id'))
        if Subscription.objects.filter(user=self.request.user,
                                       author=author).exists():
            raise ValidationError([
                'Нельзя подписаться на одного и того же автора дважды'])
        if author == self.request.user:
            raise ValidationError([
                'Нельзя подписаться на самого себя'])
        follow = Subscription.objects.create(user=request.user, author=author)
        serializer = SubscriptionsUserSerializer(follow)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        """Удаление рецепта
        из списка избранного
        """
        author = get_object_or_404(
            User, id=self.kwargs.get('follow_id'))
        if Subscription.objects.filter(user=self.request.user,
                                       author=author).exists():
            Subscription.objects.filter(user=self.request.user,
                                        author=author
                                        ).delete()
            return Response([
                    'Автор успешно удален из подписок'],
                    status=status.HTTP_204_NO_CONTENT)
        raise ValidationError([
                'Автора нет в подписках'])


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientListSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        if self.action in ('patch', 'create'):
            return RecipeCreateSerializer
        return RecipeCreateSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        return download_shopping(self, request)


class FavoriteViewSet(CreateDeleteFavorite):
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()


class SubscriptionsUserViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionsUserSerializer
    queryset = Subscription.objects.all()
    permission_classes = (OwnerOrAdmins, )

    def get_serializer_class(self):
        if self.action in ('list'):
            return SubscriptionsUserSerializer
        raise ValidationError([
                'Метод запрещен'])


class SubscriptionsCreateViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionsUserSerializer
    queryset = Subscription.objects.all()


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    queryset = Shopping.objects.all()
