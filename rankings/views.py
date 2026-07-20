from django.shortcuts import render

from accounts.models import User
from games.views.attack import get_or_create_user_avatars


def ranking(request):
    users = list(User.objects.order_by('-total_score', 'username'))

    avatars_map = get_or_create_user_avatars(request, users)

    for user in users:
        user.avatar_url = avatars_map.get(str(user.id))
        
    return render(request, 'rankings/ranking.html', {
        'top_users': users[:3],
        'rest_users': users[3:],
    })