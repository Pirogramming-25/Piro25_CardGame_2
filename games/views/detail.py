import random

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from games.models import Game
from games.views.attack import get_or_create_user_avatars

CARD_RANGE = range(1, 11)
CARD_COUNT = 5


@login_required
def game_detail(request, pk):
    game = get_object_or_404(
        Game.objects.select_related('attacker', 'defender', 'winner'), pk=pk,
    )

    if request.user.id not in (game.attacker_id, game.defender_id):
        return HttpResponseForbidden()

    avatars_map = get_or_create_user_avatars(request, [game.attacker, game.defender])

    is_attacker = request.user.id == game.attacker_id
    is_finished = game.status == Game.Status.FINISHED

    my_card = game.attacker_card if is_attacker else game.defender_card
    opponent_card = None
    result = None
    score_delta = None

    if is_finished:
        opponent_card = game.defender_card if is_attacker else game.attacker_card
        if game.winner_id is None:
            result, score_delta = 'DRAW', 0
        elif game.winner_id == request.user.id:
            result, score_delta = 'WIN', my_card
        else:
            result, score_delta = 'LOSE', -my_card

    if is_finished:
        page_state = 'finished'
    elif is_attacker:
        page_state = 'waiting_attacker'
    else:
        page_state = 'waiting_defender'

    context = {
        'game': game,
        'opponent': game.defender if is_attacker else game.attacker,
        'is_attacker': is_attacker,
        'page_state': page_state,
        'my_card': my_card,
        'opponent_card': opponent_card,
        'result': result,
        'score_delta': score_delta,
        'can_counter': game.status == Game.Status.WAITING and not is_attacker,
        'attacker_avatar': avatars_map.get(str(game.attacker.id)),
        'defender_avatar': avatars_map.get(str(game.defender.id)),
    }
    return render(request, 'games/game_detail.html', context)


@login_required
def game_status(request, pk):
    """진행중 화면에서 상대의 반격 완료 여부를 폴링으로 확인하기 위한 엔드포인트."""
    game = get_object_or_404(Game, pk=pk)

    if request.user.id not in (game.attacker_id, game.defender_id):
        return HttpResponseForbidden()

    return JsonResponse({'status': game.status})


@login_required
def counter_attack(request, pk):
    game = get_object_or_404(Game, pk=pk)

    if request.user.id != game.defender_id:
        return HttpResponseForbidden()
    if game.status != Game.Status.WAITING:
        return redirect('games:detail', pk=game.pk)

    session_key = f'counter_cards_{game.pk}'

    if request.method == 'POST':
        offered_cards = request.session.get(session_key)
        card = request.POST.get('card')

        try:
            card = int(card)
        except (TypeError, ValueError):
            return HttpResponseBadRequest('유효하지 않은 카드 선택입니다.')

        if not offered_cards or card not in offered_cards:
            return HttpResponseBadRequest('유효하지 않은 카드 선택입니다.')

        with transaction.atomic():
            # WAITING 상태인 게임만 골라 FINISHED로 선점 — 동시에 반격 요청이
            # 중복으로 들어와도 한쪽만 판정을 실행하도록 막는다.
            claimed = Game.objects.filter(
                pk=game.pk, status=Game.Status.WAITING,
            ).update(status=Game.Status.FINISHED)

            if not claimed:
                return redirect('games:detail', pk=game.pk)

            game = Game.objects.get(pk=game.pk)
            game.resolve(card)

        del request.session[session_key]
        return redirect('games:detail', pk=game.pk)

    cards = random.sample(CARD_RANGE, CARD_COUNT)
    request.session[session_key] = cards
    return render(request, 'games/counter.html', {'game': game, 'cards': cards})
