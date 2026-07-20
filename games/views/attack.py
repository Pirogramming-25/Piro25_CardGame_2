import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth import get_user_model
from games.models import Game

User = get_user_model()


def get_or_create_user_avatars(request, users):
    if 'user_avatars' not in request.session:
        request.session['user_avatars'] = {}

    user_avatars = dict(request.session['user_avatars'])
    avatar_list = [f'/static/games/images/avatar/user{i}.png' for i in range(1, 6)]
    
    updated = False
    for user in users:
        str_id = str(user.id)
        if str_id not in user_avatars:
            user_avatars[str_id] = random.choice(avatar_list)
            updated = True

    if updated:
        request.session['user_avatars'] = user_avatars
        request.session.modified = True

    return user_avatars

def attack_card_view(request):
    if request.method == 'POST':
        # 💡 터미널에 전달받은 POST 데이터 전체 출력
        print("=== POST DATA ===", request.POST)
        
        card = request.POST.get('card')
        print("=== CARD VALUE ===", repr(card)) # 값의 형태(None, "", "5" 등) 확인

        try:
            card = int(card)
        except (TypeError, ValueError):
            # 💡 에러 원인을 화면에 구체적으로 보여주도록 수정
            return HttpResponseBadRequest(f"유효하지 않은 카드입니다. (전달된 값: '{card}')")

        request.session['selected_card'] = card
        request.session.modified = True
        return redirect('games:attack_user')

    cards = random.sample(range(1, 11), 5)
    cards.sort()

    context = {'cards': cards}
    return render(request, 'games/attack_card.html', context)


def attack_user_view(request):
    if request.method == 'POST':
        defender_id = request.POST.get('defender_id')
        attacker_card = request.session.get('selected_card')

        # 💡 원인 파악용 디버깅 응답
        if not attacker_card:
            return HttpResponseBadRequest(f" [에러] 카드가 세션에 없습니다. (현재 세션 카드: {attacker_card})")
        
        if not defender_id or defender_id == "undefined":
            return HttpResponseBadRequest(f" [에러] 유저 ID가 전달되지 않았습니다. (전달된 ID: '{defender_id}')")

        try:
            defender = get_object_or_404(User, id=defender_id)
        except Exception as e:
            return HttpResponseBadRequest(f" [에러] 해당 ID({defender_id})의 유저를 DB에서 찾을 수 없습니다.")

        # ... 이하 게임 생성 로직 동일
        # if not defender_id or not attacker_card:
        #     return HttpResponseBadRequest('카드 또는 상대 선택 정보가 유효하지 않습니다.')

        defender = get_object_or_404(User, id=defender_id)

        win_condition = random.choice([
            Game.WinCondition.HIGH, 
            Game.WinCondition.LOW
        ])

        game = Game.objects.create(
            attacker=request.user,
            defender=defender,
            attacker_card=attacker_card,
            win_condition=win_condition,
            status=Game.Status.WAITING
        )

        if 'selected_card' in request.session:
            del request.session['selected_card']

        # 💡 status가 아닌 detail 페이지로 redirect!
        return redirect('games:detail', pk=game.pk)

    if request.user.is_authenticated:
        db_users = User.objects.exclude(id=request.user.id)
    else:
        db_users = User.objects.all()

    avatars_map = get_or_create_user_avatars(request, db_users)

    users_with_avatar = []
    for user in db_users:
        users_with_avatar.append({
            'id': user.id,
            'name': user.username,
            'avatar_url': avatars_map.get(str(user.id)),
        })

    context = {'users': users_with_avatar}
    return render(request, 'games/attack_user.html', context)