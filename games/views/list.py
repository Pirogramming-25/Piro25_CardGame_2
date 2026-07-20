from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from games.models import Game


def _field_name(*candidates):
    fields = {field.name for field in Game._meta.get_fields()}
    return next((name for name in candidates if name in fields), None)


def _is_pending(game, defender_card_field, status_field):
    if defender_card_field:
        return getattr(game, defender_card_field, None) is None
    if status_field:
        status = str(getattr(game, status_field, '')).lower()
        return status in {'pending', 'waiting', 'requested', 'progress'}
    return True


def _result_for(game, user, winner_field, status_field):
    winner = getattr(game, winner_field, None) if winner_field else None
    if winner_field and winner is None:
        return 'draw'
    if winner is not None:
        winner_id = getattr(winner, 'pk', winner)
        return 'win' if winner_id == user.pk else 'lose'
    status = str(getattr(game, status_field, '')).lower() if status_field else ''
    if status in {'draw', 'tie'}:
        return 'draw'
    if status in {'finished', 'completed', 'done'}:
        return 'finished'
    return None


def _game_rows(user):
    attacker_field = _field_name('attacker', 'challenger', 'initiator', 'requester')
    defender_field = _field_name('defender', 'opponent', 'target', 'receiver')
    if not attacker_field or not defender_field:
        return []

    defender_card_field = _field_name('defender_card', 'counter_card', 'defense_card', 'opponent_card')
    status_field = _field_name('status', 'state')
    winner_field = _field_name('winner', 'winning_user')
    ordering_field = _field_name('created_at', 'created', 'requested_at')
    games = Game.objects.filter(
        Q(**{attacker_field: user}) | Q(**{defender_field: user})
    ).select_related(attacker_field, defender_field)
    games = games.order_by(f'-{ordering_field}' if ordering_field else '-pk')

    rows = []
    for game in games:
        attacker = getattr(game, attacker_field)
        defender = getattr(game, defender_field)
        pending = _is_pending(game, defender_card_field, status_field)
        is_attacker = attacker.pk == user.pk
        rows.append({
            'id': game.pk,
            'attacker': attacker,
            'defender': defender,
            'pending': pending,
            'can_cancel': pending and is_attacker,
            'can_counter': pending and not is_attacker,
            'result': None if pending else _result_for(game, user, winner_field, status_field),
        })
    return rows


@login_required
@require_http_methods(['GET', 'POST'])
def game_list(request):
    if request.method == 'POST':
        game_id = request.POST.get('cancel_id')
        attacker_field = _field_name('attacker', 'challenger', 'initiator', 'requester')
        defender_card_field = _field_name('defender_card', 'counter_card', 'defense_card', 'opponent_card')
        status_field = _field_name('status', 'state')
        if not game_id or not attacker_field:
            raise Http404
        try:
            game = Game.objects.get(pk=game_id, **{attacker_field: request.user})
        except (Game.DoesNotExist, ValueError):
            raise Http404
        if not _is_pending(game, defender_card_field, status_field):
            raise Http404
        game.delete()
        return redirect('games:game_list')

    paginator = Paginator(_game_rows(request.user), 4)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'games/game_list.html', {'page_obj': page_obj})
