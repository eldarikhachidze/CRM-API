from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Table, CloseFloot, Hall, GameDay
from .serializers import TableSerializer, CloseFlootSerializer, HallSerializer, GameDaySerializer



class TableListCreate(generics.ListCreateAPIView):
    queryset = Table.objects.all().order_by('name')
    serializer_class = TableSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Table has been Added."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TableRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({"message": "Table has been Updated."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Table has been Deleted."}, status=status.HTTP_200_OK)

class AddTableToHall(generics.UpdateAPIView):
    def put(self, request, table_id, hall_id):
        try:
            # Get the table and hall objects
            table = Table.objects.get(pk=table_id)
            hall = Hall.objects.get(pk=hall_id)
        except Table.DoesNotExist:
            return Response({"message": "Table does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Hall.DoesNotExist:
            return Response({"message": "Hall does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Assign the hall to the table
        table.hall = hall
        table.save()

        return Response({"message": "Table has been added to Hall."}, status=status.HTTP_200_OK)

class RemoveTableFromHall(generics.UpdateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def put(self, request, *args, **kwargs):
        try:
            table = Table.objects.get(pk=kwargs['pk'])
        except Table.DoesNotExist:
            return Response({"message": "Table does not exist."}, status=status.HTTP_404_NOT_FOUND)

        table.hall = None
        table.save()
        return Response({"message": "Table has been removed from Hall."}, status=status.HTTP_200_OK)


class HallListCreate(generics.ListCreateAPIView):
    queryset = Hall.objects.all().order_by('name')
    serializer_class = HallSerializer

class CloseFlootCreateView(generics.CreateAPIView):
    queryset = CloseFloot.objects.all()
    serializer_class = CloseFlootSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "table has been closed."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CloseFlootRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = CloseFloot.objects.all()
    serializer_class = CloseFlootSerializer


class CreateGameDayView(APIView):
    def post(self, request):
        date = request.data.get('date')
        if not date:
            return Response({'message': 'Date is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a GameDay already exists for the date
        game_day, created = GameDay.objects.get_or_create(date=date)

        if not created:
            return Response({'message': 'GameDay already exists for this date.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create CloseFloot entries for each hall's tables
        halls = Hall.objects.all()
        for hall in halls:
            tables = Table.objects.filter(hall=hall)
            for table in tables:
                CloseFloot.objects.create(
                    table=table,
                    game_day=game_day,
                    close_flot_total=0.0,
                    close_flot={}  # Initialize with empty or default close_flot data
                )

        return Response({'message': 'GameDay created and CloseFloot entries added.'}, status=status.HTTP_201_CREATED)


class GameDayListView(generics.RetrieveAPIView):
    queryset = GameDay.objects.all()
    serializer_class = GameDaySerializer

    def get_object(self):
        return self.queryset.latest('created_at')