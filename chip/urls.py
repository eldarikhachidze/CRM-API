from django.urls import path
from .views import ChipListCreate, ChipDetailUpdateDelete


urlpatterns = [
    path('', ChipListCreate.as_view(), name='chip-list'),
    path('<int:pk>/', ChipDetailUpdateDelete.as_view(), name='chipmodel-detail-update-delete'),
]