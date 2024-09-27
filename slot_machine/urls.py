from django.urls import path
from .views import SlotMachineListCreateView, SlotMachineCreateView

urlpatterns = [
    path('slotmachines/', SlotMachineListCreateView.as_view(), name='slotmachine-list-create'),
    path('slotMachine/create/', SlotMachineCreateView.as_view(), name='slot_machine-create'),
]