from django.contrib import admin
from .models import Table, CloseFloot, Hall, GameDayLive

# Register your models here.


admin.site.register(Table)
admin.site.register(CloseFloot)
admin.site.register(Hall)
admin.site.register(GameDayLive)