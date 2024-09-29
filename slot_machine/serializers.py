from rest_framework import serializers
from .models import SlotMachine




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

class SlotMachineBvbMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = SlotMachine
        fields = ['bvbMoney']

    def validate_bvbMoney(self, value):
        if value < 0:
            raise serializers.ValidationError("Bvb Money cannot be negative.")
        return value