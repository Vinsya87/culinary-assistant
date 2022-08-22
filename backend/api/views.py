from app.models import (Favorite, Ingredient, Recipe, RecipeIngredientAmount,
                        Shopping, Subscription, Tag)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from users.models import User

from api.permissions import OwnerOrAdmins
from api.serializers import (FavoriteSerializer, IngredientListSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             SubscriptionsUserSerializer, TagSerializer)

from .filter import IngredientSearchFilter, RecipeFilter


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
        final_list = {}
        ingredients = RecipeIngredientAmount.objects.filter(
            recipe__purchases__user=request.user).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount'
        )
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                final_list[name]['amount'] += item[2]
        pdfmetrics.registerFont(
            TTFont('Handicraft', 'data/Handicraft Regular.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="Recipes.pdf"')
        page = canvas.Canvas(response)
        page.setFont('Handicraft', size=24)
        page.drawString(200, 800, 'Список покупок')
        page.setFont('Handicraft', size=16)
        height = 750
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(75, height, (f'{i}. {name} - {data["amount"]} '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()

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


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    queryset = Shopping.objects.all()

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

