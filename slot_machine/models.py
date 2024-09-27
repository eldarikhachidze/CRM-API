from django.db import models
from django.utils import timezone
# Create your models here.

class SlotMachine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=100)
    bvbMoney = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


