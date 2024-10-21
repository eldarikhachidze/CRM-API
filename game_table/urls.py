from django.urls import path
from .views import (
    TableListCreate,
    TableRetrieveUpdateDestroy,
    CloseFlootListCreate,
    CloseFlootRetrieveUpdateDestroy
)

urlpatterns = [
    path('create/', TableListCreate.as_view(), name='table-list-create'),
    path('delete/<int:pk>/', TableRetrieveUpdateDestroy.as_view(), name='table-detail'),
    path('close-flots/', CloseFlootListCreate.as_view(), name='close-flot-list-create'),
    path('close-flots/<int:pk>/', CloseFlootRetrieveUpdateDestroy.as_view(), name='close-flot-detail'),
]