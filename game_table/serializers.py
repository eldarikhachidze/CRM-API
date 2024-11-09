from rest_framework import serializers
from django.utils import timezone
from .models import Table, CloseFloot, Hall, GameDayLive, Plaque, TableResult
import logging

logger = logging.getLogger(__name__)


class CloseFlootSerializer(serializers.ModelSerializer):
    table_id = serializers.IntegerField(write_only=True)  # Direct mapping for input
    game_day = serializers.IntegerField(write_only=True)  # Direct mapping for input
    close_flot = serializers.DictField(child=serializers.IntegerField())

    class Meta:
        model = CloseFloot
        fields = [
            'table_id',
            'game_day',  # Added this line to include game_day
            'close_flot',
            'close_flot_total',
            'result',
            'close_date',
            'status',
            'fill_credit',
            'created_at',
            'updated_at',
            'deleted_at'
        ]

    def create(self, validated_data):
        # Extract table_id, game_day_id, and close_flot from validated_data
        table_id = validated_data.pop('table_id')
        game_day_id = validated_data.pop('game_day')
        close_flot = validated_data.pop('close_flot')

        # Calculate close_flot_total
        close_flot_total = sum(
            float(denomination) * float(quantity)
            for denomination, quantity in close_flot.items()
            if isinstance(quantity, (int, float))
        )

        # Retrieve the Table instance
        try:
            table = Table.objects.get(id=table_id)
            open_flot_total = table.open_flot_total
        except Table.DoesNotExist:
            raise serializers.ValidationError({"table_id": "Table with this ID does not exist."})

        # Retrieve the GameDay instance by ID
        try:
            game_day_instance = GameDayLive.objects.get(id=game_day_id)
        except GameDayLive.DoesNotExist:
            raise serializers.ValidationError({"game_day": "GameDay with this ID does not exist."})

        # Check if CloseFloot entry already exists for this table and game day
        try:
            close_floot_instance = CloseFloot.objects.get(table=table, game_day=game_day_instance)

            close_floot_instance.close_flot = close_flot
            close_floot_instance.close_flot_total = close_flot_total
            close_floot_instance.result = close_flot_total - open_flot_total
            close_floot_instance.status = False
            close_floot_instance.close_date = timezone.now()
            close_floot_instance.save()
        except CloseFloot.DoesNotExist:
            # If no existing entry, create a new one
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

        # Update or create the corresponding TableResult entry
        table_result, created = TableResult.objects.get_or_create(
            table=table, game_day=game_day_instance
        )
        table_result.result = close_floot_instance.result
        table_result.save()

        return close_floot_instance

    def update(self, instance, validated_data):
        table_id = validated_data.pop('table_id')
        game_day_id = validated_data.pop('game_day')
        close_flot = validated_data.pop('close_flot')
        close_flot_total = sum(
            float(denomination) * float(quantity)
            for denomination, quantity in close_flot.items()
            if isinstance(quantity, (int, float))
        )

        open_flot_total = instance.table.open_flot_total
        latest_close_floot = instance.table.closefloot_set.last()

        latest_close_floot.close_flot = close_flot
        latest_close_floot.close_flot_total = close_flot_total
        latest_close_floot.result = close_flot_total - open_flot_total
        latest_close_floot.status = validated_data.get('status', instance.status)
        latest_close_floot.close_date = timezone.now()
        latest_close_floot.updated_at = timezone.now()
        latest_close_floot.save()

        table_result, created = TableResult.objects.get_or_create(
            table=table_id, game_day=game_day_id
        )
        table_result.result = latest_close_floot.result
        table_result.save()

        return instance


class TableSerializer(serializers.ModelSerializer):
    hall = serializers.CharField(source='hall.name', read_only=True)
    latest_close_floot = serializers.SerializerMethodField()
    latest_plaque = serializers.SerializerMethodField()
    last_result = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ['id', 'name', 'open_flot', 'open_flot_total', 'hall', 'latest_close_floot', 'latest_plaque',
                  'last_result']

    def get_last_result(self, obj):
        try:
            last_result = TableResult.objects.filter(table=obj).latest('created_at')
            return last_result.result
        except TableResult.DoesNotExist:
            return 0.0

    def get_latest_plaque(self, obj):
        latest_plaque = obj.plaque_set.order_by('-created_at').first()
        return PlaqueSerializer(latest_plaque).data if latest_plaque else None

    def get_latest_close_floot(self, obj):
        close_floot_instance = obj.closefloot_set.last()
        if close_floot_instance:
            close_floot_data = CloseFlootSerializer(close_floot_instance).data
            # Add game_day field here
            close_floot_data['game_day'] = close_floot_instance.game_day.id  # Adjust the field as needed
            return close_floot_data
        return None

    def create(self, validated_data):
        open_flot = validated_data.get('open_flot', {})
        sorted_open_flot = dict(sorted(open_flot.items(), key=lambda x: float(x[0])))

        open_flot_total = sum(
            float(denomination) * float(quantity) for denomination, quantity in sorted_open_flot.items() if
            isinstance(quantity, (int, float)))

        validated_data['open_flot'] = sorted_open_flot
        validated_data['open_flot_total'] = open_flot_total

        table = Table.objects.create(**validated_data)
        return table

    def update(self, instance, validated_data):
        open_flot = validated_data.get('open_flot', {})
        sorted_open_flot = dict(sorted(open_flot.items(), key=lambda x: float(x[0])))

        open_flot_total = sum(
            float(denomination) * float(quantity) for denomination, quantity in sorted_open_flot.items() if
            isinstance(quantity, (int, float)))

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


class PlaqueSerializer(serializers.ModelSerializer):
    table_id = serializers.IntegerField(write_only=True)  # Direct mapping for input
    game_day = serializers.IntegerField(write_only=True)  # Direct mapping for input

    class Meta:
        model = Plaque
        fields = ['table_id', 'game_day', 'plaques', 'plaques_total', 'result', 'status', 'created_at', 'updated_at',
                  'deleted_at']

    def create(self, validated_data):
        table_id = validated_data.pop('table_id')
        game_day_id = validated_data.pop('game_day')
        plaques = validated_data.pop('plaques', {})

        plaques_total = sum(
            float(denomination) * float(quantity)
            for denomination, quantity in plaques.items()
            if isinstance(quantity, (int, float))
        )

        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            raise serializers.ValidationError({"table_id": "Table with this ID does not exist."})

        try:
            game_day_instance = GameDayLive.objects.get(id=game_day_id)
        except GameDayLive.DoesNotExist:
            raise serializers.ValidationError({"game_day": "GameDay with this ID does not exist."})

        try:
            last_result = TableResult.objects.filter(table=table, game_day=game_day_instance).latest('created_at')
        except TableResult.DoesNotExist:
            raise serializers.ValidationError(
                {"table_id": "Table with this ID does not have a result for this game day."})

        plaque_instance = Plaque.objects.create(
            table=table,
            status=True,
            game_day=game_day_instance,
            plaques=plaques,
            plaques_total=plaques_total,
            result=plaques_total,
            **validated_data
        )

        TableResult.objects.create(
            table=table,
            game_day=game_day_instance,
            result=plaques_total + last_result.result
        )

        return plaque_instance

    def update(self, instance, validated_data):
        instance.plaques = validated_data.get('plaques', instance.plaques)
        instance.plaques_total = validated_data.get('plaques_total', instance.plaques_total)
        instance.result = validated_data.get('result', instance.result)
        instance.updated_at = timezone.now()

        instance.save()
        return instance


class GameDayLiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameDayLive
        fields = '__all__'
