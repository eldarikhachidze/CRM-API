from django.shortcuts import render
from rest_framework import generics
from .models import SlotMachine
from .serializers import SlotMachineSerializer

# Create your views here.


class SlotMachineListCreateView(generics.ListAPIView):
    queryset = SlotMachine.objects.all()
    serializer_class = SlotMachineSerializer

class SlotMachineCreateView(generics.CreateAPIView):
    queryset = SlotMachine.objects.all()
    serializer_class = SlotMachineSerializer

    # Override the post method to handle creation
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()  # Save the new object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

