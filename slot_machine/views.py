from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import SlotMachine, Hall, GameDay, DailyAmount
from .serializers import SlotMachineSerializer, HallSerializer, GameDaySerializer, DailyAmountSerializer

# Create your views here.


class HallListCreateView(generics.ListCreateAPIView):
    queryset = Hall.objects.all()
    serializer_class = HallSerializer

class FullDatabaseView(APIView):

    def get(self, request, *args, **kwargs):
        halls = Hall.objects.all()
        game_days = GameDay.objects.all()

        hall_serializer = HallSerializer(halls, many=True)
        game_day_serializer = GameDaySerializer(game_days, many=True)

        data = {
            'halls': hall_serializer.data,
            'game_days': game_day_serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)

class SlotMachineListCreateView(generics.ListCreateAPIView):
    queryset = SlotMachine.objects.all()
    serializer_class = SlotMachineSerializer

class GameDayListCreateView(generics.ListCreateAPIView):
    queryset = GameDay.objects.all()
    serializer_class = GameDaySerializer

class GameDayRetrieveView(generics.RetrieveAPIView):
    queryset = GameDay.objects.all()
    serializer_class = GameDaySerializer
    lookup_field = 'id'

class HallsWithSlotMachinesView(APIView):
    def get(self, request, *args, **kwargs):
        halls = Hall.objects.prefetch_related('slot_machines').all()
        serializer = HallSerializer(halls, many=True)
        return Response(serializer.data)

class DailyAmountListCreateView(generics.ListCreateAPIView):
    queryset = DailyAmount.objects.all()
    serializer_class = DailyAmountSerializer

# Retrieve, Update, and Delete DailyAmount objects
class DailyAmountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DailyAmount.objects.all()
    serializer_class = DailyAmountSerializer
    lookup_field = 'id'