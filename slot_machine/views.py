from django.db.models import Prefetch
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .models import SlotMachine, Hall, GameDay, DailyAmount
from .serializers import SlotMachineSerializer, HallSerializer, GameDaySerializer, DailyAmountSerializer

# Create your views here.


class HallListView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the start_date and end_date from the request query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # If no date range is provided, use the most recent GameDay
        if not start_date or not end_date:
            try:
                # Fetch the most recent GameDay
                latest_game_day = GameDay.objects.latest('date')
                start_date = end_date = latest_game_day.date.isoformat()
            except GameDay.DoesNotExist:
                return Response({"error": "No GameDay record exists."}, status=status.HTTP_404_NOT_FOUND)

        # Prefetch related slot machines and daily amounts, filter by the specified or latest date range
        halls = Hall.objects.prefetch_related(
            Prefetch('slot_machines__daily_amounts', queryset=DailyAmount.objects.filter(game_day__date__range=[start_date, end_date]))
        ).distinct()
        # Pass the context with the date range
        serializer = HallSerializer(halls, many=True, context={
                'start_date': start_date,
                'end_date': end_date
            })
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrentGameDayView(APIView):

    def get(self, request, *args, **kwargs):
        # Get the most recent GameDay
        try:
            current_game_day = GameDay.objects.latest('date')
        except GameDay.DoesNotExist:
            return Response({"error": "No GameDay record exists."}, status=status.HTTP_404_NOT_FOUND)

        halls = Hall.objects.all()

        total_daily_amount = 0
        hall_data = []

        # Iterate through halls and slot machines
        for hall in halls:
            slot_machines = []

            for slot_machine in hall.slot_machines.all():
                # Filter to get only the daily amount for the current game day
                daily_amount = slot_machine.daily_amounts.filter(game_day=current_game_day).first()

                if daily_amount:
                    total_daily_amount += daily_amount.amount

                    slot_machine_data = {
                        'id': slot_machine.id,
                        'name': slot_machine.name,
                        'brand': slot_machine.brand,
                        'daily_amounts': [{'id': daily_amount.id, 'amount': daily_amount.amount}]
                    }
                    slot_machines.append(slot_machine_data)

            hall_data.append({
                'id': hall.id,
                'name': hall.name,
                'daily_money_sum': sum(slot['daily_amounts'][0]['amount'] for slot in slot_machines),
                'slot_machines': slot_machines
            })

        # Serialize the current game day
        game_day_serializer = GameDaySerializer(current_game_day)

        # Prepare the response data
        data = {
            'halls': hall_data,
            'game_day': [game_day_serializer.data],  # Only return the current game day
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


class CloseOpenGameDayView(APIView):

    def get(self, request, *args, **kwargs):
        game_days = GameDay.objects.all()
        serializer = GameDaySerializer(game_days, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Get the current date from the request
        current_date = request.data.get('date')
        print(f"Current Date from Frontend: {current_date}")

        if not current_date:
            return Response({"error": "Date is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the current date exists in the GameDay model
            game_day_exists = GameDay.objects.filter(date=current_date).exists()

            if game_day_exists:
                # If the current game day exists, create a new day with the next day date
                new_date = (datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=1)).date()
                print(f"New Date to be created: {new_date}")
            else:
                # If the current date doesn't exist, set it as the new date
                new_date = current_date

            # Create or get the new GameDay object
            game_day, created = GameDay.objects.get_or_create(date=new_date)

            if not created:
                return Response({"error": "A Game Day with this date already exists."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch all slot machines for which DailyAmount needs to be created
            slot_machines = SlotMachine.objects.all()

            if not slot_machines.exists():
                return Response({"error": "No slot machines found to create DailyAmount entries."}, status=status.HTTP_400_BAD_REQUEST)

            # Prepare and create DailyAmount for each slot machine
            daily_amounts = [
                DailyAmount(slot_machine=slot_machine, game_day=game_day, amount=0.00)
                for slot_machine in slot_machines
            ]
            DailyAmount.objects.bulk_create(daily_amounts)

            return Response({"message": "New GameDay created and DailyAmount records added."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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

