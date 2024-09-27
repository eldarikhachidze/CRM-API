from django.urls import path
from .views import ChipListView


urlpatterns = [
    path('chip', ChipListView.as_view(), name='chip-list'),
]