from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    total_score = models.IntegerField(default=0)  # 누적 점수