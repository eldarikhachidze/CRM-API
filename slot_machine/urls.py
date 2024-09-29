from django.urls import path
from .views import SlotMachineListCreateView, SlotMachineBvbMoneyUpdateView

urlpatterns = [
    path('slotmachines/', SlotMachineListCreateView.as_view(), name='slotmachine-list-create'),
    path('slot-machine/<int:pk>/close/', SlotMachineBvbMoneyUpdateView.as_view(), name='slot-machine-close')
]