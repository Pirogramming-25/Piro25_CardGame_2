from django.db import models
from django.conf import settings


class Game(models.Model):
    # ⚠️ 첫날 팀 회의에서 확정한 필드 작성
    # User 참조는 settings.AUTH_USER_MODEL 사용
    pass