# urls.py
from django.urls import path
from .views import (
    HallListView,
    SlotMachineListCreateView, 
    GameDayListCreateView, 
    DailyAmountListCreateView, 
    GameDayRetrieveView,
    FullDatabaseView,
    HallsWithSlotMachinesView,
    DailyAmountListCreateView,
    DailyAmountRetrieveUpdateDestroyView
)

urlpatterns = [
    path('halls/', HallListView.as_view(), name='hall-list-create'),
    path('slot-machines/', SlotMachineListCreateView.as_view(), name='slot-machine-list-create'),
    path('game-days/', GameDayListCreateView.as_view(), name='game-day-list-create'),
    path('game-days/<int:id>/', GameDayRetrieveView.as_view(), name='game-day-retrieve'),
    path('daily-amounts/', DailyAmountListCreateView.as_view(), name='daily-amount-list-create'),
    path('full-database/', FullDatabaseView.as_view(), name='full-database'),
    path('halls-with-slot-machines/', HallsWithSlotMachinesView.as_view(), name='halls-with-slot-machines'),
    path('daily-amounts/', DailyAmountListCreateView.as_view(), name='daily-amount-list-create'),
    path('daily-amounts/<int:id>/', DailyAmountRetrieveUpdateDestroyView.as_view(), name='daily-amount-retrieve-update-destroy'),


]
