from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from .models import FillCredit
from .serializers import FillCreditSerializer
from game_table.models import GameDayLive, TableResult


# Create your views here.


class FillCreditListCreate(generics.ListCreateAPIView):
    serializer_class = FillCreditSerializer

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date and end_date:
            try:
                start_date = GameDayLive.objects.get(date=start_date)
            except GameDayLive.DoesNotExist:
                raise NotFound({"message": "Start date does not exist."})

            try:
                end_date = GameDayLive.objects.get(date=end_date)
            except GameDayLive.DoesNotExist:
                raise NotFound({"message": "End date does not exist."})

            return FillCredit.objects.filter(game_day__date__gte=start_date.date, game_day__date__lte=end_date.date)

        else:
            try:
                current_game_day = GameDayLive.objects.latest('date')
                start_date = current_game_day
                end_date = current_game_day
            except GameDayLive.DoesNotExist:
                raise NotFound({"message": "Game Day does not exist."})

            return FillCredit.objects.filter(game_day__date__gte=start_date.date, game_day__date__lte=end_date.date)




        return FillCredit.objects.filter(game_day__date__gte=start_date, game_day__date__lte=end_date)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Fill Credit has been Added."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FillCreditRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = FillCredit.objects.all()
    serializer_class = FillCreditSerializer

    def put(self, request, *args, **kwargs):
        try:
            fill_credit = FillCredit.objects.get(pk=kwargs['pk'])
        except FillCredit.DoesNotExist:
            return Response({"message": "Fill Credit does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Update the serializer with game_day if provided
        serializer = self.get_serializer(fill_credit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Fill Credit has been updated."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            fill_credit = FillCredit.objects.get(pk=kwargs['pk'])
        except FillCredit.DoesNotExist:
            return Response({"message": "Fill Credit does not exist."}, status=status.HTTP_404_NOT_FOUND)

        try:
            table_result = TableResult.objects.get(table=fill_credit.table, game_day=fill_credit.game_day)
        except TableResult.DoesNotExist:
            return Response({"message": "Table Result does not exist."}, status=status.HTTP_404_NOT_FOUND)

        table_result.result -= fill_credit.fill_credit
        table_result.save()

        fill_credit.delete()

        return Response({"message": "Fill Credit has been deleted."}, status=status.HTTP_200_OK)
