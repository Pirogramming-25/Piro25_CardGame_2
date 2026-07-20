from django.shortcuts import render

from accounts.models import User


def ranking(request):
    users = User.objects.order_by('-total_score', 'username')
    return render(request, 'rankings/ranking.html', {
        'top_users': users[:3],
        'rest_users': users[3:],
    })