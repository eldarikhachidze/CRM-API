from rest_framework import serializers
from .models import ChipModel

class ChipModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChipModel
        fields = '__all__'

    def validate_name(self, value):
        # Normalize data: strip whitespace and convert to lower case for consistent validation
        value = value.strip().lower()

        # Check if the name already exists in the database
        try:
            float(value)
        except ValueError:
            raise serializers.ValidationError("The name field must be a number.")

        return value


    def validate_denomination(self, value):
        if value == 0:
            raise serializers.ValidationError("Denomination cannot be zero.")
        if value < 0:
            raise serializers.ValidationError("Denomination cannot be negative.")
        return value
