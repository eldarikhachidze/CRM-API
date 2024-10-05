from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import SlotMachine, Hall, GameDay, DailyAmount
from .serializers import SlotMachineSerializer, HallSerializer, GameDaySerializer, DailyAmountSerializer

# Create your views here.


class HallListView(APIView):
    def get(self, request, *args, **kwargs):
        halls = Hall.objects.prefetch_related('slot_machines__daily_amounts').all()
        serializer = HallSerializer(halls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FullDatabaseView(APIView):

    def get(self, request, *args, **kwargs):
        halls = Hall.objects.all()
        game_days = GameDay.objects.all()

        total_daily_amount = sum(
            daily.amount for hall in halls
            for slot_machine in hall.slot_machines.all()
            for daily in slot_machine.daily_amounts.all()
        )

        hall_serializer = HallSerializer(halls, many=True)
        game_day_serializer = GameDaySerializer(game_days, many=True)

        data = {
            'halls': hall_serializer.data,
            'game_days': game_day_serializer.data,
            'total_daily_amount': total_daily_amount
        }

        return Response(data, status=status.HTTP_200_OK)

class SlotMachineListCreateView(APIView):
    def get(self, request, *args, **kwargs):
        slot_machines = SlotMachine.objects.all()
        serializer = SlotMachineSerializer(slot_machines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = SlotMachineSerializer(data=request.data)

        if serializer.is_valid():
            # Check if hall is provided, otherwise set to None (null)
            hall_id = serializer.validated_data.get('hall', None)

            if hall_id:
                hall = Hall.objects.get(id=hall_id)
            else:
                hall = None

            # Create or get the SlotMachine object with hall possibly being None
            slot_machine, created = SlotMachine.objects.get_or_create(
                name=serializer.validated_data['name'],
                brand=serializer.validated_data['brand'],
                hall=hall  # This can be None
            )

            if not created:
                return Response({"error": "Slot Machine with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the most recent GameDay from the database
            try:
                recent_game_day = GameDay.objects.latest('date')
            except GameDay.DoesNotExist:
                return Response({"error": "No GameDay record exists. Please create a GameDay first."}, status=status.HTTP_400_BAD_REQUEST)

            # Automatically create DailyAmount object for the new SlotMachine
            DailyAmount.objects.create(
                slot_machine=slot_machine,
                game_day=recent_game_day,
                amount=0.00  # Default amount is 0
            )

            return Response({"message": "Slot Machine and DailyAmount have been created."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SlotMachineChangeAmountMoneyView(APIView):
    def put(self, request, *args, **kwargs):
        slot_machine_id = kwargs.get('slot_machine_id')
        amount = request.data.get('amount')

        # Ensure amount is provided and is not None or empty
        if amount is None or amount == "":
            return Response({"error": "Amount cannot be null or empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)  # Ensure it's a valid number
        except ValueError:
            return Response({"error": "Invalid amount. Please provide a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slot_machine = SlotMachine.objects.get(id=slot_machine_id)
        except SlotMachine.DoesNotExist:
            return Response({"error": "Slot Machine not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            recent_game_day = GameDay.objects.latest('date')
        except GameDay.DoesNotExist:
            return Response({"error": "No GameDay record exists. Please create a GameDay first."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            daily_amount = DailyAmount.objects.get(
                slot_machine=slot_machine,
                game_day=recent_game_day
            )
        except DailyAmount.DoesNotExist:
            return Response({"error": "DailyAmount record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the amount and save it
        daily_amount.amount = amount
        daily_amount.save()

        return Response({"message": "Slot closed successfully."}, status=status.HTTP_200_OK)

class SlotMachineDeleteView(APIView):
    def delete(self, request, *args, **kwargs):
        slot_machine_id = kwargs.get('slot_machine_id')

        try:
            slot_machine = SlotMachine.objects.get(id=slot_machine_id)
        except SlotMachine.DoesNotExist:
            return Response({"error": "Slot Machine not found."}, status=status.HTTP_404_NOT_FOUND)

        slot_machine.delete()

        return Response({"message": "Slot Machine has been deleted."}, status=status.HTTP_200_OK)


class SlotMachineAddToHallView(APIView):
    def put(self, request, *args, **kwargs):
        slot_machine_id = kwargs.get('slot_machine_id')
        hall_id = kwargs.get('hall_id')

        try:
            slot_machine = SlotMachine.objects.get(id=slot_machine_id)
        except SlotMachine.DoesNotExist:
            return Response({"error": "Slot Machine not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            hall = Hall.objects.get(id=hall_id)
        except Hall.DoesNotExist:
            return Response({"error": "Hall not found."}, status=status.HTTP_404_NOT_FOUND)

        slot_machine.hall = hall
        slot_machine.save()

        return Response({"message": f"Slot Machine {slot_machine.name} has been added to Hall {hall.name}."}, status=status.HTTP_200_OK)


class SlotMachineRemoveFromHallView(APIView):
    def put(self, request, *args, **kwargs):
        slot_machine_id = kwargs.get('slot_machine_id')

        try:
            slot_machine = SlotMachine.objects.get(id=slot_machine_id)
        except SlotMachine.DoesNotExist:
            return Response({"error": "Slot Machine not found."}, status=status.HTTP_404_NOT_FOUND)

        # Remove slot machine from the hall (set hall to None)
        slot_machine.hall = None
        slot_machine.save()

        return Response({"message": f"Slot Machine {slot_machine.name} has been removed from its hall."}, status=status.HTTP_200_OK)


class GameDayListCreateView(APIView):
    def get(self, request, *args, **kwargs):
        game_days = GameDay.objects.all()
        serializer = GameDaySerializer(game_days, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = GameDaySerializer(data=request.data)
        print(f"Request Data: {request.data}")

        if serializer.is_valid():
            date = serializer.validated_data['date']
            print(f"Date: {date}")
            game_day, created = GameDay.objects.get_or_create(date=date)
            print(f"Game Day: {game_day}, Created: {created}")

            if not created:
                return Response({"error": "A Game Day with this date already exists."}, status=status.HTTP_400_BAD_REQUEST)

            slot_machines = SlotMachine.objects.all()

            # Ensure there are slot machines to create DailyAmount for
            if not slot_machines.exists():
                return Response({"error": "No slot machines found to create DailyAmount entries."}, status=status.HTTP_400_BAD_REQUEST)

            for slot_machine in slot_machines:
                try:
                    # Create DailyAmount for each slot machine
                    daily_amount = DailyAmount.objects.create(
                        slot_machine=slot_machine,
                        game_day=game_day,
                        amount=0.00  # Default amount to 0
                    )
                    print(f"Created DailyAmount for Slot Machine {slot_machine.id} on Game Day {game_day.date}")
                except Exception as e:
                    print(f"Error creating DailyAmount for Slot Machine {slot_machine.id}: {str(e)}")

            return Response({"message": "GameDay created and DailyAmount records added."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class GameDayRetrieveView(generics.RetrieveAPIView):
    queryset = GameDay.objects.all()
    serializer_class = GameDaySerializer
    lookup_field = 'id'

class HallsWithSlotMachinesView(APIView):
    def get(self, request, *args, **kwargs):
        halls = Hall.objects.prefetch_related('slot_machines').all()
        serializer = HallSerializer(halls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DailyAmountListCreateView(generics.ListCreateAPIView):
    queryset = DailyAmount.objects.all()
    serializer_class = DailyAmountSerializer

# Retrieve, Update, and Delete DailyAmount objects
class DailyAmountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DailyAmount.objects.all()
    serializer_class = DailyAmountSerializer
    lookup_field = 'id'

