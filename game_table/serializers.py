from rest_framework import serializers
from django.utils import timezone
from .models import Table, CloseFloot, Hall, GameDay

class CloseFlootSerializer(serializers.ModelSerializer):
    table_id = serializers.IntegerField(write_only=True)  # Direct mapping for input
    game_day = serializers.IntegerField(write_only=True)  # Direct mapping for input

    class Meta:
        model = CloseFloot
        fields = ['table_id', 'game_day', 'close_flot', 'close_flot_total', 'result', 'close_date', 'status', 'plaques', 'plaques_total', 'fill_credit', 'created_at', 'updated_at', 'deleted_at']

    def create(self, validated_data):
        print("Validated data received:", validated_data)  # For debugging

        # Extract table_id and game_day_id from validated_data
        table_id = validated_data.pop('table_id')
        game_day_id = validated_data.pop('game_day')
        close_flot = validated_data.pop('close_flot')  # Extract close_flot explicitly

        # Calculate close_flot_total
        close_flot_total = sum(
            float(denomination) * float(quantity)
            for denomination, quantity in close_flot.items()
            if isinstance(quantity, (int, float))
        )
        print("Close flot total:", close_flot_total)  # For debugging

        # Retrieve the Table instance
        try:
            table = Table.objects.get(id=table_id)
            open_flot_total = table.open_flot_total
        except Table.DoesNotExist:
            raise serializers.ValidationError({"table_id": "Table with this ID does not exist."})

        # Retrieve the GameDay instance by ID
        try:
            game_day_instance = GameDay.objects.get(id=game_day_id)
        except GameDay.DoesNotExist:
            raise serializers.ValidationError({"game_day": "GameDay with this ID does not exist."})

        # Create the CloseFloot instance
        close_floot_instance = CloseFloot.objects.create(
            table=table,
            status=False,
            game_day=game_day_instance,
            close_flot=close_flot,
            close_flot_total=close_flot_total,
            close_date=timezone.now(),
            result=close_flot_total - open_flot_total,
            **validated_data
        )
        return close_floot_instance

    def update(self, instance, validated_data):
        # Update the instance fields
        instance.close_flot = validated_data.get('close_flot', instance.close_flot)
        instance.close_flot_total = validated_data.get('close_flot_total', instance.close_flot_total)
        instance.result = validated_data.get('result', instance.result)
        instance.status = validated_data.get('status', instance.status)
        instance.updated_at = timezone.now()

        instance.save()
        return instance



class TableSerializer(serializers.ModelSerializer):
    hall = serializers.CharField(source='hall.name', read_only=True)
    latest_close_floot = serializers.SerializerMethodField()


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


    def get_latest_close_floot(self, obj):
        # Get the latest close_floot record for this table
        latest_close_floot = obj.closefloot_set.order_by('-created_at').first()
        return CloseFlootSerializer(latest_close_floot).data if latest_close_floot else None


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

class HallSerializer(serializers.ModelSerializer):
    tables = TableSerializer(many=True, read_only=True, source='table_set')
    class Meta:
        model = Hall
        fields = ['id', 'name', 'created_at', 'updated_at', 'deleted_at', 'tables']

    def validate_name(self, value):
        if self.instance:
            return value

        if not value:
            raise serializers.ValidationError("The name field cannot be empty.")

        if Hall.objects.filter(name=value).exists():
            raise serializers.ValidationError("A Hall with this name already exists.")

        return value




class GameDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = GameDay
        fields = '__all__'