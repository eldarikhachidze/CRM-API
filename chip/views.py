from rest_framework import generics
from .models import ChipModel
from .serializers import ChipModelSerializer

class ChipListView(generics.ListAPIView):
    queryset = ChipModel.objects.all()
    serializer_class = ChipModelSerializer


