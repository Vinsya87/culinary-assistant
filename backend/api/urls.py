from django.urls import include, path, re_path
# from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from api.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingCartViewSet, SubscriptionsCreateViewSet,
                       SubscriptionsUserViewSet, TagViewSet)

app_name = 'api'

router = DefaultRouter()
# router.register('userss', CustomUserViewSet, basename='user')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(
    r'recipes/(?P<recipe_id>[\d]+)/favorite',
    FavoriteViewSet,
    basename='favorite',
)
router.register(
    'users/subscriptions', SubscriptionsUserViewSet, basename='subscriptions')
router.register(
    r'users/(?P<follow_id>[\d]+)/subscribe',
    SubscriptionsCreateViewSet,
    basename='subscribes',
)
router.register(
    r'recipes/(?P<shop_id>[\d]+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_carts',
)
urlpatterns = [
    path('', include(router.urls)),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.jwt')),
    # re_path(r'^auth/', include('djoser.urls')),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    # path('api-token-auth/', CustomAuthToken.as_view())
]
