from django.urls import path
from .views import attack

from games.views import detail

app_name = 'games'

urlpatterns = [
    # 각자 담당 뷰 연결할 때 한 줄씩만 추가
    path('<int:pk>/', detail.game_detail, name='detail'),
    path('<int:pk>/status/', detail.game_status, name='status'),
    path('<int:pk>/counter/', detail.counter_attack, name='counter'),
    path('attack/', attack.attack_card_view, name='attack_card'),
    path('attack/user/', attack.attack_user_view, name='attack_user'),
]