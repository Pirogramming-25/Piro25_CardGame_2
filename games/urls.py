from django.urls import path
from games.views.list import game_list

app_name = 'games'

urlpatterns = [
    path('', game_list, name='game_list'),
    # 각자 담당 뷰 연결할 때 한 줄씩만 추가
]
