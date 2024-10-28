from django.db import models
from django.utils import timezone

# Create your models here.

class Table(models.Model):
    name = models.CharField(max_length=200, unique=True)
    open_flot_total = models.FloatField(default=0.0)
    hall = models.ForeignKey('Hall', on_delete=models.CASCADE, null=True, blank=True)
    result = models.FloatField(default=0.0)  # Add this line if it's missing
    date_created = models.DateTimeField(default=timezone.now)
    date_edited = models.DateTimeField(null=True, blank=True)
    date_deleted = models.DateTimeField(null=True, blank=True)
    open_flot = models.JSONField(default=dict)  # Default to an empty JSON object

    def __str__(self):
        return f"Table: {self.name}"


class CloseFloot(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    game_day = models.ForeignKey('GameDay', on_delete=models.CASCADE)
    close_flot_total = models.FloatField(default=0.0)
    result = models.FloatField(default=0.0)  # Add this line if it's missing
    close_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    close_flot = models.JSONField(default=dict)  # Default to an empty JSON object

    def __str__(self):
        return f"Table: {self.table.name}"

class Hall(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class GameDay(models.Model):
    date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.date)