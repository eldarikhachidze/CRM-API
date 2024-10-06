from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from .models import SlotMachine, Hall, GameDay, DailyAmount



class DailyAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAmount
        fields = '__all__'

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount cannot be negative.")
        return value

class SlotMachineSerializer(serializers.ModelSerializer):
    daily_amounts = DailyAmountSerializer(many=True, read_only=True)
    class Meta:
        model = SlotMachine
        fields = '__all__'


    def create(self, validated_data):
        # Create the SlotMachine object
        slot_machine = SlotMachine.objects.create(**validated_data)

        # Get or create the most recent GameDay
        game_day, created = GameDay.objects.get_or_create(
            date=timezone.now().date()
        )

        # Automatically create DailyAmount for the newly created SlotMachine
        try:
            DailyAmount.objects.create(
                slot_machine=slot_machine,
                game_day=game_day,
                amount=0.00  # Default amount set to 0
            )
        except Exception as e:
            raise serializers.ValidationError(f"An error occurred: {e}")

        return slot_machine

    # Validate the name field for uniqueness
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("The name field cannot be empty.")
        if SlotMachine.objects.filter(name=value).exists():
            raise serializers.ValidationError("A Slot Machine with this name already exists.")
        return value



class HallSerializer(serializers.ModelSerializer):
    slot_machines = serializers.SerializerMethodField()  # We'll process the slot machines separately
    daily_money_sum = serializers.SerializerMethodField()
    slot_machines_by_brand = serializers.SerializerMethodField()

    class Meta:
        model = Hall
        fields = '__all__'

    def get_slot_machines(self, obj):
        current_game_day = GameDay.objects.latest('date')
        slot_machines_data = []

        for slot_machine in obj.slot_machines.all():
            # Filter to get only the daily amount for the current game day
            daily_amount = slot_machine.daily_amounts.filter(game_day=current_game_day).first()

            if daily_amount:
                slot_machines_data.append({
                    'id': slot_machine.id,
                    'name': slot_machine.name,
                    'brand': slot_machine.brand,
                    'daily_amount': daily_amount.amount,  # Only return the daily amount for the current day
                })

        return slot_machines_data

    def get_slot_machines_by_brand(self, obj):
        brand_data = {}
        current_game_day = GameDay.objects.latest('date')

        for slot_machine in obj.slot_machines.all():
            # Get the daily amount for the current game day
            daily_amount = slot_machine.daily_amounts.filter(game_day=current_game_day).first()
            if not daily_amount:
                continue

            brand = slot_machine.brand
            daily_total = daily_amount.amount

            if brand in brand_data:
                brand_data[brand]['count'] += 1
                brand_data[brand]['total_money'] += daily_total
            else:
                brand_data[brand] = {
                    'count': 1,
                    'total_money': daily_total
                }

        return brand_data

    def get_daily_money_sum(self, obj):
        current_game_day = GameDay.objects.latest('date')
        total_daily_amount = sum(
            daily.amount for slot_machine in obj.slot_machines.all()
            for daily in slot_machine.daily_amounts.filter(game_day=current_game_day)
        )
        return total_daily_amount


class GameDaySerializer(serializers.ModelSerializer):
    daily_amounts_by_game_day = DailyAmountSerializer(many=True)
    class Meta:
        model = GameDay
        fields = '__all__'

    # Validate the date field for uniqueness
    def validate_date(self, value):
        if not value:
            raise serializers.ValidationError("The date field cannot be empty.")
        if GameDay.objects.filter(date=value).exists():
            raise serializers.ValidationError("A Game Day with this date already exists.")
        return value

class FullDatabaseSerializer(serializers.Serializer):
    halls = HallSerializer(many=True)
    game_days = GameDaySerializer(many=True)