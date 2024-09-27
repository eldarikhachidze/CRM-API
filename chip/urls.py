from django.urls import path
from .views import ChipListView


urlpatterns = [
    path('', ChipListView.as_view(), name='chip-list'),
]