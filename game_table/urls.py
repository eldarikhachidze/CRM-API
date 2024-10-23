from django.urls import path
from .views import (
    TableListCreate,
    TableRetrieveUpdateDestroy,
    CloseFlootListCreate,
    CloseFlootRetrieveUpdateDestroy,
    HallListCreate,
    AddTableToHall,
    RemoveTableFromHall,
)

urlpatterns = [
    path('create/', TableListCreate.as_view(), name='table-list-create'),
    path('delete/<int:pk>/', TableRetrieveUpdateDestroy.as_view(), name='table-detail'),
    path('close-flots/', CloseFlootListCreate.as_view(), name='close-flot-list-create'),
    path('close-flots/<int:pk>/', CloseFlootRetrieveUpdateDestroy.as_view(), name='close-flot-detail'),
    path('hall/', HallListCreate.as_view(), name='hall-list-create'),
    path('add-to-hall/<int:table_id>/<int:hall_id>/', AddTableToHall.as_view(), name='add-table-to-hall'),
    path('remove-from-hall/<int:pk>/', RemoveTableFromHall.as_view(), name='remove-table-from-hall'),
]