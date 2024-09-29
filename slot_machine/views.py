from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import SlotMachine
from .serializers import SlotMachineSerializer, SlotMachineBvbMoneySerializer

# Create your views here.


class SlotMachineListCreateView(generics.ListAPIView):
    queryset = SlotMachine.objects.all()
    serializer_class = SlotMachineSerializer



class SlotMachineBvbMoneyUpdateView(generics.UpdateAPIView):
    queryset = SlotMachine.objects.all()
    serializer_class = SlotMachineBvbMoneySerializer
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        try:
            slot_machine = self.get_object()
            serializer = self.get_serializer(slot_machine, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "BVB Money updated successfully!"  # Make sure message is included
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SlotMachine.DoesNotExist:
            return Response({
                "error": True,
                "message": "SlotMachine not found."  # Error message included here
            }, status=status.HTTP_404_NOT_FOUND)