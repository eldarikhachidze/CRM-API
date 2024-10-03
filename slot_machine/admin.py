from django.contrib import admin
from .models import SlotMachine, Hall, GameDay, DailyAmount

# Register your models here.


admin.site.register(SlotMachine)
admin.site.register(Hall)
admin.site.register(GameDay)
admin.site.register(DailyAmount)

