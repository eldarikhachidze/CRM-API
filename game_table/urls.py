from django.urls import path
from .views import (
    TableListCreate,
    TableRetrieveUpdateDestroy,
    CloseFlootCreateView,
    CloseFlootRetrieveUpdateDestroy,
    HallListCreate,
    AddTableToHall,
    RemoveTableFromHall,
    CreateGameDayView,
    GameDayListView,
    PlaqueCreateView,
    PlaqueRetrieveUpdateDestroy,
)

urlpatterns = [
    path('create/', TableListCreate.as_view(), name='table-list-create'),
    path('delete/<int:pk>/', TableRetrieveUpdateDestroy.as_view(), name='table-detail'),
    path('close-table/', CloseFlootCreateView.as_view(), name='close-flot-list-create'),
    path('close-table/<int:pk>/', CloseFlootRetrieveUpdateDestroy.as_view(), name='close-flot-detail'),
    path('plaque/', PlaqueCreateView.as_view(), name='plaque-list-create'),
    path('plaque/<int:pk>/', PlaqueRetrieveUpdateDestroy.as_view(), name='plaque-detail'),
    path('hall/', HallListCreate.as_view(), name='hall-list-create'),
    path('add-to-hall/<int:table_id>/<int:hall_id>/', AddTableToHall.as_view(), name='add-table-to-hall'),
    path('remove-from-hall/<int:pk>/', RemoveTableFromHall.as_view(), name='remove-table-from-hall'),
    path('create-game-day/', CreateGameDayView.as_view(), name='create-game-day'),
    path('game-day/', GameDayListView.as_view(), name='game-day-list'),
]