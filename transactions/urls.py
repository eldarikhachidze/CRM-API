from django.urls import path
from .views import FillCreditListCreate


urlpatterns = [
    path('fill-credit/', FillCreditListCreate.as_view(), name='fill-credit-list-create'),
]