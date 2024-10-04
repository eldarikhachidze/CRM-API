from rest_framework import serializers
from .models import SlotMachine, Hall, GameDay, DailyAmount




class DailyAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAmount
        fields = '__all__'

class SlotMachineSerializer(serializers.ModelSerializer):
    daily_amounts = DailyAmountSerializer(many=True, read_only=True)
    class Meta:
        model = SlotMachine
        fields = '__all__'

    # Validate the name field for uniqueness
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("The name field cannot be empty.")
        if SlotMachine.objects.filter(name=value).exists():
            raise serializers.ValidationError("A Slot Machine with this name already exists.")
        return value


class HallSerializer(serializers.ModelSerializer):
    slot_machines = SlotMachineSerializer(many=True, read_only=True)
    daily_money_sum = serializers.SerializerMethodField()
    class Meta:
        model = Hall
        fields = '__all__'

    def get_daily_money_sum(self, obj):
        total_daily_amount = sum(
            daily.amount for slot_machines in obj.slot_machines.all()
            for daily in slot_machines.daily_amounts.all()
        )
        return total_daily_amount

    # Validate the name field for uniqueness
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("The name field cannot be empty.")
        if Hall.objects.filter(name=value).exists():
            raise serializers.ValidationError("A Hall with this name already exists.")
        return value


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