from django.conf import settings
from django.db import models
from django.utils import timezone


class Game(models.Model):
    class WinCondition(models.TextChoices):
        HIGH = 'HIGH', '높은 숫자 승리'
        LOW = 'LOW', '낮은 숫자 승리'

    class Status(models.TextChoices):
        WAITING = 'WAITING', '반격 대기중'
        FINISHED = 'FINISHED', '종료'

    attacker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attacking_games',
    )
    defender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='defending_games',
    )

    attacker_card = models.PositiveSmallIntegerField()
    defender_card = models.PositiveSmallIntegerField(null=True, blank=True)

    # 승리 조건은 공격(게임 생성) 시점에 랜덤으로 확정되어 저장된다.
    win_condition = models.CharField(max_length=10, choices=WinCondition.choices)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.WAITING)
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='won_games',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.attacker} -> {self.defender} ({self.get_status_display()})'

    def resolve(self, defender_card):
        """수비자의 카드를 받아 승패를 판정하고 양쪽 점수에 반영한 뒤 저장한다."""
        self.defender_card = defender_card

        if self.attacker_card == defender_card:
            self.winner = None
        elif self.win_condition == self.WinCondition.HIGH:
            self.winner = self.attacker if self.attacker_card > defender_card else self.defender
        else:
            self.winner = self.attacker if self.attacker_card < defender_card else self.defender

        if self.winner is not None:
            if self.winner_id == self.attacker_id:
                winner_card, loser, loser_card = self.attacker_card, self.defender, defender_card
            else:
                winner_card, loser, loser_card = defender_card, self.attacker, self.attacker_card

            self.winner.total_score += winner_card
            loser.total_score -= loser_card
            self.winner.save(update_fields=['total_score'])
            loser.save(update_fields=['total_score'])

        self.status = self.Status.FINISHED
        self.finished_at = timezone.now()
        self.save()
