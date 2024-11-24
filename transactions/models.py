from django.db import models
from django.utils import timezone
from datetime import timedelta
from game_table.models import Table, GameDayLive


def adjusted_now():
    return timezone.now() + timedelta(hours=4)
# Create your models here.


class FillCredit(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    game_day = models.ForeignKey(GameDayLive, on_delete=models.CASCADE)
    action_time = models.DateTimeField(null=True, blank=True)
    fill_credit = models.FloatField(default=0.0)
    result = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=adjusted_now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"FillCredit: {self.fill_credit}"
