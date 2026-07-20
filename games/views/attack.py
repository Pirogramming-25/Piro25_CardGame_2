# views.py
from django.shortcuts import render
# from accounts.models import User
import random

def attack_card_view(request):
    cards = random.sample(range(1, 11), 5)
    cards.sort()

    context = {
        'cards': cards,
    }
    return render(request, 'games/attack_card.html', context)

def attack_user_view(request):
    # avatar_list = [
    #     f'/static/games/images/avatar/user{i}.png' for i in range(1, 6)
    # ]
    
    # if request.user.is_authenticated:
    #     db_users = User.objects.exclude(id=request.user.id)
    # else:
    #     db_users = User.objects.all()

    # users_with_avatar = []
    # for user in db_users:
    #     users_with_avatar.append({
    #         'id': user.id,
    #         'name': user.username,
    #         'avatar_url': random.choice(avatar_list),
    #     })

    # context = {
    #     'users': users_with_avatar,
    # }

    dummy_users = [
        {'name': 'user1', 'avatar_url': '/static/games/images/avatar/user1.png'},
        {'name': 'user2', 'avatar_url': '/static/games/images/avatar/user2.png'},
        {'name': 'user3', 'avatar_url': '/static/games/images/avatar/user3.png'},
        {'name': 'user4', 'avatar_url': '/static/games/images/avatar/user4.png'},
        {'name': 'user5', 'avatar_url': '/static/games/images/avatar/user5.png'},
    ]

    context = {
        'users': dummy_users,
    }
    return render(request, 'games/attack_user.html', context)