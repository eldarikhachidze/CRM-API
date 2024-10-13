from django.db import models
from django.utils import timezone

# Create your models here.

class ChipModel(models.Model):
    denomination = models.FloatField(unique=True)
    date_created = models.DateTimeField(default=timezone.now)  # Set default to current time
    date_edited = models.DateTimeField(null=True, blank=True)
    date_deleted = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.denomination}"