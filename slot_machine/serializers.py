from rest_framework import serializers
from .models import SlotMachine, Hall, GameDay, DailyAmount




class SlotMachineSerializer(serializers.ModelSerializer):
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

class DailyAmountSerializer(serializers.ModelSerializer):
    slot_machine = SlotMachineSerializer()
    class Meta:
        model = DailyAmount
        fields = '__all__'

class HallSerializer(serializers.ModelSerializer):
    slot_machines = SlotMachineSerializer(many=True)
    class Meta:
        model = Hall
        fields = '__all__'

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


