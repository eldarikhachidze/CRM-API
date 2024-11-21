from rest_framework import serializers
from .models import FillCredit
from game_table.models import TableResult, GameDayLive
from django.utils import timezone


class FillCreditSerializer(serializers.ModelSerializer):
    table_name = serializers.SerializerMethodField()
    game_date = serializers.SerializerMethodField()
    game_day = serializers.PrimaryKeyRelatedField(queryset=GameDayLive.objects.all())

    class Meta:
        model = FillCredit
        fields = '__all__'

    def get_table_name(self, obj):
        return obj.table.name if obj.table else None

    def get_game_date(self, obj):
        return obj.game_day.date if obj.game_day else None

    def get(self, request):
        return self.get(request)

    def create(self, validated_data):
        table_id = validated_data.pop('table')
        game_day_data = validated_data.pop('game_day')

        fill_credit_amount = validated_data.pop('fill_credit')

        if isinstance(game_day_data, GameDayLive):
            game_day_id = game_day_data.id
        else:
            game_day_id = game_day_data

        action_time = validated_data.pop('action_time', None)

        if action_time:
            if action_time.tzinfo is None:
                action_time = timezone.make_aware(action_time, timezone.get_current_timezone())
        else:
            action_time = timezone.now()

        table_result, created = TableResult.objects.get_or_create(
            table=table_id, game_day_id=game_day_id
        )

        fill_credit = FillCredit.objects.create(
            table=table_id,
            game_day_id=game_day_id,
            fill_credit=fill_credit_amount,
            action_time=action_time
        )

        table_result.result += fill_credit_amount
        table_result.save()

        return fill_credit

    def update(self, instance, validated_data):
        fill_credit_id = instance.id
        new_fill_credit = validated_data.get('fill_credit', instance.fill_credit)
        table_id = validated_data.get('table', instance.table)
        game_day_id = validated_data.get('game_day', instance.game_day)
        action_time = validated_data.get('action_time', instance.action_time)

        if action_time is None:
            action_time = timezone.now()

        try:
            table_result = TableResult.objects.get(table=table_id, game_day=game_day_id)
        except TableResult.DoesNotExist:
            raise serializers.ValidationError({"message": "Table Result does not exist."})

        old_fill_credit = instance.fill_credit
        table_result.result -= old_fill_credit
        table_result.result += new_fill_credit
        table_result.save()

        instance.fill_credit = new_fill_credit
        instance.table = table_id
        instance.game_day = game_day_id
        instance.action_time = action_time
        instance.save()

        return instance

    def delete(self, instance):
        table_id = instance.table
        game_day_id = instance
        fill_credit_amount = instance.fill_credit

        try:
            table_result = TableResult.objects.get(table=table_id, game_day=game_day_id)
        except TableResult.DoesNotExist:
            raise serializers.ValidationError({"message": "Table Result does not exist."})

        table_result.result -= fill_credit_amount
        table_result.save()

        instance.delete()
        return instance
