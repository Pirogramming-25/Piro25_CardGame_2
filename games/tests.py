from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from games.models import Game

User = get_user_model()


class GameDetailTests(TestCase):
    def setUp(self):
        self.attacker = User.objects.create_user(username='attacker', password='pass1234')
        self.defender = User.objects.create_user(username='defender', password='pass1234')
        self.stranger = User.objects.create_user(username='stranger', password='pass1234')
        self.game = Game.objects.create(
            attacker=self.attacker, defender=self.defender,
            attacker_card=7, win_condition=Game.WinCondition.HIGH,
        )

    def test_stranger_cannot_view_detail(self):
        self.client.login(username='stranger', password='pass1234')
        response = self.client.get(reverse('games:detail', args=[self.game.id]))
        self.assertEqual(response.status_code, 403)

    def test_status_endpoint_reflects_game_state(self):
        self.client.login(username='attacker', password='pass1234')
        response = self.client.get(reverse('games:status', args=[self.game.id]))
        self.assertEqual(response.json(), {'status': 'WAITING'})

        self.game.resolve(3)
        response = self.client.get(reverse('games:status', args=[self.game.id]))
        self.assertEqual(response.json(), {'status': 'FINISHED'})

    def test_stranger_cannot_view_status(self):
        self.client.login(username='stranger', password='pass1234')
        response = self.client.get(reverse('games:status', args=[self.game.id]))
        self.assertEqual(response.status_code, 403)

    def test_defender_can_counter_attacker_cannot(self):
        self.client.login(username='defender', password='pass1234')
        response = self.client.get(reverse('games:detail', args=[self.game.id]))
        self.assertTrue(response.context['can_counter'])

        self.client.login(username='attacker', password='pass1234')
        response = self.client.get(reverse('games:detail', args=[self.game.id]))
        self.assertFalse(response.context['can_counter'])

    def test_counter_rejects_card_not_offered(self):
        self.client.login(username='defender', password='pass1234')
        response = self.client.get(reverse('games:counter', args=[self.game.id]))
        offered = response.context['cards']
        not_offered = next(c for c in range(1, 11) if c not in offered)

        response = self.client.post(reverse('games:counter', args=[self.game.id]), {'card': not_offered})
        self.assertEqual(response.status_code, 400)

    def test_counter_rejects_non_numeric_card_without_crashing(self):
        self.client.login(username='defender', password='pass1234')
        self.client.get(reverse('games:counter', args=[self.game.id]))

        response = self.client.post(reverse('games:counter', args=[self.game.id]), {'card': 'abc'})
        self.assertEqual(response.status_code, 400)

    def test_counter_resolves_and_updates_scores(self):
        self.client.login(username='defender', password='pass1234')
        response = self.client.get(reverse('games:counter', args=[self.game.id]))
        offered = response.context['cards']

        response = self.client.post(reverse('games:counter', args=[self.game.id]), {'card': offered[0]})
        self.assertRedirects(response, reverse('games:detail', args=[self.game.id]))

        self.game.refresh_from_db()
        self.attacker.refresh_from_db()
        self.defender.refresh_from_db()

        self.assertEqual(self.game.status, Game.Status.FINISHED)
        self.assertEqual(self.game.defender_card, offered[0])

        if self.game.attacker_card == self.game.defender_card:
            self.assertIsNone(self.game.winner)
            self.assertEqual(self.attacker.total_score, 0)
            self.assertEqual(self.defender.total_score, 0)
        elif self.game.winner_id == self.attacker.id:
            self.assertEqual(self.attacker.total_score, self.game.attacker_card)
            self.assertEqual(self.defender.total_score, -self.game.defender_card)
        else:
            self.assertEqual(self.defender.total_score, self.game.defender_card)
            self.assertEqual(self.attacker.total_score, -self.game.attacker_card)

    def test_cannot_counter_twice(self):
        self.client.login(username='defender', password='pass1234')
        response = self.client.get(reverse('games:counter', args=[self.game.id]))
        offered = response.context['cards']
        self.client.post(reverse('games:counter', args=[self.game.id]), {'card': offered[0]})

        response = self.client.get(reverse('games:counter', args=[self.game.id]))
        self.assertRedirects(response, reverse('games:detail', args=[self.game.id]))
