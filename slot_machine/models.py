from django.db import models
from django.utils import timezone

class GameDay(models.Model):
    date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.date)

class SlotMachine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=100)
    hall = models.ForeignKey('Hall', related_name='slot_machines', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class Hall(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def total_daily_amounts(self):
            total_amount = DailyAmount.objects.filter(slot_machine__hall=self).aggregate(total=models.Sum('amount'))['total']
            return total_amount or 0

class DailyAmount(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    slot_machine = models.ForeignKey(SlotMachine, related_name='daily_amounts', on_delete=models.CASCADE)
    game_day = models.ForeignKey(GameDay, related_name='daily_amounts_by_game_day', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} on {self.slot_machine} for {self.game_day}"
