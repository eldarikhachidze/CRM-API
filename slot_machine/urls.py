# urls.py
from django.urls import path
from .views import (
    HallListView,
    SlotMachineListCreateView, 
    CloseOpenGameDayView,
    DailyAmountListCreateView, 
    GameDayRetrieveView,
    CurrentGameDayView,
    HallsWithSlotMachinesView,
    DailyAmountListCreateView,
    DailyAmountRetrieveUpdateDestroyView,
    SlotMachineAddToHallView,
    SlotMachineRemoveFromHallView,
    SlotMachineDetailUpdateDeleteView,
    SlotMachineChangeAmountMoneyView
)

urlpatterns = [
    #+
    path('halls/', HallListView.as_view(), name='hall-list-create'),
    #+
    path('slot-machine/', SlotMachineListCreateView.as_view(), name='slot-machine-list-create'),
    #+
    path('close-game-day/', CloseOpenGameDayView.as_view(), name='close-game-day'),
    path('game-days/<int:id>/', GameDayRetrieveView.as_view(), name='game-day-retrieve'),
    path('daily-amounts/', DailyAmountListCreateView.as_view(), name='daily-amount-list-create'),
    #+
    path('game_date/', CurrentGameDayView.as_view(), name='full-database'),
    path('halls-with-slot-machines/', HallsWithSlotMachinesView.as_view(), name='halls-with-slot-machines'),
    path('daily-amounts/', DailyAmountListCreateView.as_view(), name='daily-amount-list-create'),
    path('daily-amounts/<int:id>/', DailyAmountRetrieveUpdateDestroyView.as_view(), name='daily-amount-retrieve-update-destroy'),
    path('add-slot-to-hall/<int:slot_machine_id>/<int:hall_id>/', SlotMachineAddToHallView.as_view(), name='add-slot-machine-to-hall'),
    #+
    path('remove-slot-from-hall/<int:slot_machine_id>/', SlotMachineRemoveFromHallView.as_view(), name='remove-slot-machine-from-hall'),
    #+
    path('slot-machine/<int:pk>/', SlotMachineDetailUpdateDeleteView.as_view(), name='delete-slot-machine'),
    #+
    path('close-slot-machine/<int:slot_machine_id>/', SlotMachineChangeAmountMoneyView.as_view(), name='change-amount-money'),

]
