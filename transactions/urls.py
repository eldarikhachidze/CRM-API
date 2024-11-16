from django.urls import path
from .views import FillCreditListCreate, FillCreditRetrieveUpdateDestroy


urlpatterns = [
    path('fill-credit/', FillCreditListCreate.as_view(), name='fill-credit-list-create'),
    path('fill-credit/<int:pk>/', FillCreditRetrieveUpdateDestroy.as_view(), name='fill-credit-retrieve-update-destroy'),
]