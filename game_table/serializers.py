from rest_framework import serializers
from .models import Table, CloseFloot

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

    def validate_name(self, value):

        if self.instance:
            return value

        if not value:
            raise serializers.ValidationError("The name field cannot be empty.")

        if Table.objects.filter(name=value).exists():
            raise serializers.ValidationError("A Table with this name already exists.")

        return value

    def validate_open_flot(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Open flot must be a dictionary with denominations and quantities.")
        return value

    def create(self, validated_data):
        open_flot = validated_data.get('open_flot', {})
        sorted_open_flot = dict(sorted(open_flot.items(), key=lambda x: float(x[0])))

        open_flot_total = sum(float(denomination) * float(quantity) for denomination, quantity in sorted_open_flot.items() if isinstance(quantity, (int, float)))

        validated_data['open_flot'] = sorted_open_flot
        validated_data['open_flot_total'] = open_flot_total

        # Create the table instance
        table = Table.objects.create(**validated_data)
        return table

    def update(self, instance, validated_data):
        open_flot = validated_data.get('open_flot', {})
        sorted_open_flot = dict(sorted(open_flot.items(), key=lambda x: float(x[0])))

        open_flot_total = sum(float(denomination) * float(quantity) for denomination, quantity in sorted_open_flot.items() if isinstance(quantity, (int, float)))

        validated_data['open_flot'] = sorted_open_flot
        validated_data['open_flot_total'] = open_flot_total

        table = super().update(instance, validated_data)
        return table

class CloseFlootSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloseFloot
        fields = '__all__'
