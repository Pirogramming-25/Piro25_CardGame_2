from django.urls import path
from . import views

app_name = 'rankings'   # games, rankings로 각각 변경

urlpatterns = [
    path('', views.ranking, name='ranking'),
]