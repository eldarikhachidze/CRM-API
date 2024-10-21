from rest_framework import serializers
from .models import Table, CloseFloot

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

    def validate_open_flot(self, value):
        # Ensure that opening chips are provided in the correct format
        if not isinstance(value, dict):
            raise serializers.ValidationError("Open flot must be a dictionary with denominations and quantities.")
        return value

    def create(self, validated_data):
        # Sort the open_flot data by denomination before saving
        open_flot = validated_data.get('open_flot', {})
        sorted_open_flot = dict(sorted(open_flot.items(), key=lambda x: float(x[0])))

        # Update validated_data with sorted open_flot
        validated_data['open_flot'] = sorted_open_flot

        # Create the table instance
        table = Table.objects.create(**validated_data)
        return table

class CloseFlootSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloseFloot
        fields = '__all__'
