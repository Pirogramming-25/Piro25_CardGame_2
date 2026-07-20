from django.urls import path

from games.views.list import game_list
from .views import attack


app_name = 'games'

urlpatterns = [
    path('', game_list, name='game_list'),
    path('attack/', attack.attack_card_view, name='attack_card'),
    path('attack/user/', attack.attack_user_view, name='attack_user'),
]
