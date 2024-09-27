from rest_framework import serializers
from .models import ChipModel


class ChipModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChipModel
        fields = '__all__'