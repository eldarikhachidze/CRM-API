from rest_framework import serializers
from django.utils import timezone
from .models import Table, CloseFloot, Hall, GameDayLive, Plaque, TableResult
from transactions.models import FillCredit


class CloseFlootSerializer(serializers.ModelSerializer):
    table_id = serializers.IntegerField(write_only=True)
    game_day_id = serializers.IntegerField(read_only=True, source="game_day.id")
    close_flot = serializers.DictField(child=serializers.IntegerField())

    class Meta:
        model = CloseFloot
        fields = [
            'table_id',
            'game_day',
            'game_day_id',
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
        table_id = validated_data.pop('table_id')
        game_day_data = validated_data.pop('game_day')
        close_flot = validated_data.pop('close_flot')


        if isinstance(game_day_data, GameDayLive):
            game_day_id = game_day_data.id
        else:
            game_day_id = game_day_data

        for denomination, quantity in close_flot.items():
            if isinstance(quantity, (int, float)):
                if quantity < 0:
                    raise serializers.ValidationError({"message": "Close flot quantity cannot be negative."})

        close_flot_total = sum(
            float(denomination) * float(quantity)
            for denomination, quantity in close_flot.items()
            if isinstance(quantity, (int, float))
        )

        try:
            table = Table.objects.get(id=table_id)
            open_flot_total = table.open_flot_total
        except Table.DoesNotExist:
            raise serializers.ValidationError({"table_id": "Table with this ID does not exist."})

        try:
            game_day_instance = GameDayLive.objects.get(id=game_day_id)
        except GameDayLive.DoesNotExist:
            raise serializers.ValidationError({"game_day": "GameDay with this ID does not exist."})

        close_floot_instance = CloseFloot.objects.get(table=table, game_day=game_day_instance)

        close_floot_instance.close_flot = close_flot
        close_floot_instance.close_flot_total = close_flot_total
        close_floot_instance.result = close_flot_total - open_flot_total
        close_floot_instance.status = False
        close_floot_instance.close_date = timezone.now()
        close_floot_instance.save()

        table_result, created = TableResult.objects.get_or_create(
            table=table, game_day=game_day_instance
        )
        table_result.result += close_floot_instance.result
        table_result.save()

        return close_floot_instance

    def update(self, instance, validated_data):
        close_flot = validated_data.pop('close_flot')

        for denomination, quantity in close_flot.items():
            if isinstance(quantity, (int, float)):
                if quantity < 0:
                    raise serializers.ValidationError({"error": "Close flot quantity cannot be negative."})

        close_flot_total = sum(
            float(denomination) * float(quantity)
            for denomination, quantity in close_flot.items()
            if isinstance(quantity, (int, float))
        )

        table = instance.table
        game_day_instance = instance.game_day
        open_flot_total = table.open_flot_total

        table_result = TableResult.objects.get(table=table, game_day=game_day_instance)
        print('table_result.result', table_result.result)
        print('instance.result', instance.result)
        table_result.result -= instance.result
        print('table_result.result', table_result.result)

        instance.close_flot = close_flot
        print('instance.close_flot_total', instance.close_flot_total)
        print('close_flot_total', close_flot_total)
        instance.result = open_flot_total - close_flot_total
        instance.close_flot_total = close_flot_total
        instance.updated_at = timezone.now()
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        table_result.result = instance.result
        table_result.save()

        return instance


class TableSerializer(serializers.ModelSerializer):
    hall = serializers.CharField(source='hall.name', read_only=True)
    latest_close_flot = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = '__all__'

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
    tables = serializers.SerializerMethodField()

    class Meta:
        model = Hall
        fields = '__all__'

    def get_tables(self, obj):
        # Get tables related to this hall, ordered by name
        tables = obj.tables.order_by('name')
        return TableSerializer(tables, many=True, read_only=True).data

    def validate_name(self, value):
        if self.instance:
            return value

        if not value:
            raise serializers.ValidationError("The name field cannot be empty.")

        if Hall.objects.filter(name=value).exists():
            raise serializers.ValidationError("A Hall with this name already exists.")

        return value


class PlaqueSerializer(serializers.ModelSerializer):
    table_id = serializers.IntegerField(write_only=True)
    game_day = serializers.IntegerField(write_only=True)

    class Meta:
        model = Plaque
        fields = ['table_id', 'game_day', 'plaques', 'plaques_total', 'result', 'status', 'created_at', 'updated_at',
                  'deleted_at']

    def create(self, validated_data):
        table_id = validated_data.pop('table_id')
        game_day_id = validated_data.pop('game_day')
        plaques = validated_data.pop('plaques', {})

        # check if plaques quantity is negative number
        for denomination, quantity in plaques.items():
            print(denomination, quantity)
            if isinstance(quantity, (int, float)):
                if quantity < 0:
                    raise serializers.ValidationError({"error": "Plaques quantity cannot be negative."})

        plaques_total = sum(
            float(denomination) * float(quantity)
            for denomination, quantity in plaques.items()
            if isinstance(quantity, (int, float))
        )

        try:
            table = Table.objects.get(id=table_id)
            open_flot_total = table.open_flot_total
        except Table.DoesNotExist:
            raise serializers.ValidationError({"error": "Table with this ID does not exist."})

        try:
            game_day_instance = GameDayLive.objects.get(id=game_day_id)
        except GameDayLive.DoesNotExist:
            raise serializers.ValidationError({"error": "GameDay with this ID does not exist."})

        table_result, created = TableResult.objects.get_or_create(
            table=table, game_day=game_day_instance
        )

        plaque_instance = Plaque.objects.get(table=table, game_day=game_day_instance)

        plaque_instance.plaques_total = plaques_total
        plaque_instance.plaques = plaques
        plaque_instance.result = table_result.result + plaques_total
        plaque_instance.created_at = timezone.now()
        plaque_instance.status = False
        plaque_instance.save()

        table_result.result += plaques_total
        table_result.save()

        return plaque_instance

    def update(self, instance, validated_data):
        table_id = validated_data.pop('table_id')
        game_day_id = validated_data.pop('game_day')
        plaques = validated_data.pop('plaques', {})

        for denomination, quantity in plaques.items():
            print(denomination, quantity)
            if isinstance(quantity, (int, float)):
                if quantity < 0:
                    raise serializers.ValidationError({"error": "Plaques quantity cannot be negative."})

        plaques_total = sum(
            float(denomination) * float(quantity)
            for denomination, quantity in plaques.items()
            if isinstance(quantity, (int, float))
        )

        try:
            table = Table.objects.get(id=table_id)
            open_flot_total = table.open_flot_total
        except Table.DoesNotExist:
            raise serializers.ValidationError({"error": "Table with this ID does not exist."})

        try:
            game_day_instance = GameDayLive.objects.get(id=game_day_id)
        except GameDayLive.DoesNotExist:
            raise serializers.ValidationError({"error": "GameDay with this ID does not exist."})

        try:
            table_result = TableResult.objects.get(table=table, game_day=game_day_instance)
        except TableResult.DoesNotExist:
            raise serializers.ValidationError({"error": "Table Result does not exist."})

        close_flot_total = CloseFloot.objects.get(table=table, game_day=game_day_instance).close_flot_total
        open_flot_total = table.open_flot_total
        plaque_instance = Plaque.objects.get(table=table, game_day=game_day_instance)

        plaque_instance.plaques_total = plaques_total
        plaque_instance.plaques = plaques
        plaque_instance.result = plaques_total + close_flot_total - open_flot_total
        plaque_instance.updated_at = timezone.now()
        plaque_instance.save()

        table_result.result += plaque_instance.result
        table_result.save()

        return plaque_instance


class GameDayLiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameDayLive
        fields = '__all__'

class TableResultSerializer(serializers.ModelSerializer):
    table = serializers.CharField(source='table.name', read_only=True)
    game_day = serializers.CharField(source='game_day.date', read_only=True)

    class Meta:
        model = TableResult
        fields = '__all__'