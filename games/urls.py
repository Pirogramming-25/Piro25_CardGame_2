from django.urls import path

from games.views.list import game_list
from .views import attack, detail


app_name = 'games'

urlpatterns = [
    path('', game_list, name='game_list'),
    path('<int:pk>/', detail.game_detail, name='detail'),
    path('<int:pk>/status/', detail.game_status, name='status'),
    path('<int:pk>/counter/', detail.counter_attack, name='counter'),
    path('attack/', attack.attack_card_view, name='attack_card'),
    path('attack/user/', attack.attack_user_view, name='attack_user'),
]
