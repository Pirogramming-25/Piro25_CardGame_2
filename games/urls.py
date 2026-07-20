from django.urls import path

from games.views import detail

app_name = 'games'

urlpatterns = [
    # 각자 담당 뷰 연결할 때 한 줄씩만 추가
    path('<int:pk>/', detail.game_detail, name='detail'),
    path('<int:pk>/status/', detail.game_status, name='status'),
    path('<int:pk>/counter/', detail.counter_attack, name='counter'),
]