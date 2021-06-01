__author__ = 'Sergio Dzul'
from django.urls import path
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from .views import Index

urlpatterns = [
    path('', csrf_exempt(Index.as_view()), name="index"),
    # path('products/<int:pk>/recipes/', random_recipes, name="random_recipes"),
]
