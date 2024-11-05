from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Table, CloseFloot, Hall, GameDay, Plaque
from .serializers import TableSerializer, CloseFlootSerializer, HallSerializer, GameDaySerializer, PlaqueSerializer



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
        try:
            table = Table.objects.get(pk=kwargs['pk'])
        except Table.DoesNotExist:
            return Response({"message": "Table does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(table, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Table has been updated."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            table = Table.objects.get(pk=kwargs['pk'])
        except Table.DoesNotExist:
            return Response({"message": "Table does not exist."}, status=status.HTTP_404_NOT_FOUND)

        table.delete()
        return Response({"message": "Table has been deleted."}, status=status.HTTP_200_OK)



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

        # Extract the table_id and game_day from the incoming request data
        table_id = request.data.get('table_id')
        game_day_id = request.data.get('game_day')

        # Check if a CloseFloot already exists for this table and game day
        if CloseFloot.objects.filter(table_id=table_id, game_day_id=game_day_id, status=False).exists():
            return Response(
                {"error": "The table is already closed for the current game day."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Table has been closed."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CloseFlootRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = CloseFloot.objects.all()
    serializer_class = CloseFlootSerializer

    def put(self, request, pk, *args, **kwargs):
        try:
            close_floot_instance = self.get_object()
            serializer = self.get_serializer(close_floot_instance, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Close flot has been updated."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CloseFloot.DoesNotExist:
            return Response({"error": "Close flot not found."}, status=status.HTTP_404_NOT_FOUND)


class PlaqueCreateView(generics.CreateAPIView):
    queryset = Plaque.objects.all()
    serializer_class = PlaqueSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Extract the table_id and game_day from the incoming request data
        table_id = request.data.get('table_id')
        game_day_id = request.data.get('game_day')

        # Check if a Plaque already exists for this table and game day
        if Plaque.objects.filter(table_id=table_id, game_day_id=game_day_id, status=False).exists():
            return Response(
                {"error": "The table is already closed for the current game day."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Table has been closed."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaqueRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plaque.objects.all()
    serializer_class = PlaqueSerializer

    def put(self, request, pk, *args, **kwargs):
        try:
            plaque_instance = self.get_object()
            serializer = self.get_serializer(plaque_instance, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Plaque has been updated."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Plaque.DoesNotExist:
            return Response({"error": "Plaque not found."}, status=status.HTTP_404_NOT_FOUND)


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
                    status=True,
                    game_day=game_day,
                    close_flot_total=0.0,
                    close_flot={},
                ),
                Plaque.objects.create(
                    table=table,
                    status=True,
                    game_day=game_day,
                    plaques_total=0.0,
                    plaques={},
                )


        return Response({'message': 'GameDay created and CloseFloot entries added.'}, status=status.HTTP_201_CREATED)


class GameDayListView(generics.RetrieveAPIView):
    queryset = GameDay.objects.all()
    serializer_class = GameDaySerializer

    def get_object(self):
        return self.queryset.latest('created_at')