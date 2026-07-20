from django.urls import path
from .views import attack

app_name = 'games'

urlpatterns = [
    path('attack/', attack.attack_card_view, name='attack_card'),
    path('attack/user/', attack.attack_user_view, name='attack_user'),
]