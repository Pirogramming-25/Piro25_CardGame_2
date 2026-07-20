from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from games.models import Game
from games.views.attack import get_or_create_user_avatars


def _game_rows(request, user):
    games = (
        Game.objects.filter(Q(attacker=user) | Q(defender=user))
        .select_related('attacker', 'defender', 'winner')
        .order_by('-created_at')
    )

    # 1. 목록에 등장하는 모든 attacker와 defender 유저 객체들을 수집
    all_users = set()
    for game in games:
        if game.attacker:
            all_users.add(game.attacker)
        if game.defender:
            all_users.add(game.defender)

    # 2. 기존 attack.py 함수를 재활용하여 { 'user_id_str': 'avatar_url' } 맵 획득
    avatars_map = get_or_create_user_avatars(request, list(all_users))

    rows = []
    for game in games:
        pending = game.status == Game.Status.WAITING
        is_attacker = game.attacker_id == user.id

        result = None
        if not pending:
            if game.winner_id is None:
                result = 'draw'
            elif game.winner_id == user.id:
                result = 'win'
            else:
                result = 'lose'

        rows.append({
            'id': game.pk,
            'attacker': game.attacker,
            'defender': game.defender,
            'attacker_avatar': avatars_map.get(str(game.attacker_id)),
            'defender_avatar': avatars_map.get(str(game.defender_id)),
            'can_cancel': pending and is_attacker,
            'can_counter': pending and not is_attacker,
            'result': result,
        })
    return rows


@login_required(login_url='accounts:login')
@require_http_methods(['GET', 'POST'])
def game_list(request):
    if request.method == 'POST':
        game = get_object_or_404(
            Game,
            pk=request.POST.get('cancel_id'),
            attacker=request.user,
            status=Game.Status.WAITING,
        )
        game.delete()
        return redirect('games:game_list')

    paginator = Paginator(_game_rows(request, request.user), 4)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'games/game_list.html', {'page_obj': page_obj})
