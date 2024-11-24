from rest_framework import serializers
from .models import FillCredit
from game_table.models import TableResult, GameDayLive, CloseFloot
from django.utils import timezone
from datetime import timedelta


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
            if timezone.is_naive(action_time):
                action_time = timezone.make_aware(action_time, timezone.get_current_timezone())
            action_date = action_time.date()

            try:
                game_day_id = GameDayLive.objects.get(date=action_date).id
                print(game_day_id)
            except GameDayLive.DoesNotExist:
                raise serializers.ValidationError({"message": "Game Day does not exist."})
        else:
            action_time = timezone.now() + timedelta(hours=4)

        try:
            close_floot = CloseFloot.objects.filter(table=table_id, game_day_id=game_day_id).first()
        except CloseFloot.DoesNotExist:
            return serializers.ValidationError({"message": "Close Floot does not exist."})

        if fill_credit_amount < 0:
            close_floot.total_fill += fill_credit_amount
            close_floot.result += fill_credit_amount
            close_floot.save()

        elif fill_credit_amount > 0:
            close_floot.total_credit += fill_credit_amount
            close_floot.result += fill_credit_amount
            close_floot.save()
        else:
            return serializers.ValidationError({"message": "Fill Credit amount cannot be zero."})


        try:
            table_result = TableResult.objects.get(
                table=table_id, game_day_id=game_day_id
            )
        except TableResult.DoesNotExist:
            raise serializers.ValidationError({"message": "Table Result does not exist."})

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
        table_id = validated_data.pop('table', instance.table)
        game_day_data = validated_data.pop('game_day', instance.game_day)
        new_fill_credit_amount = validated_data.pop('fill_credit', instance.fill_credit)
        new_action_time = validated_data.pop('action_time', instance.action_time)

        if isinstance(game_day_data, GameDayLive):
            game_day_id = game_day_data.id
        else:
            game_day_id = game_day_data

        if timezone.is_naive(new_action_time):
            new_action_time = timezone.make_aware(new_action_time, timezone.get_current_timezone())
        action_date = new_action_time.date()

        try:
            close_floot = CloseFloot.objects.filter(table=table_id, game_day_id=game_day_id).first()
        except CloseFloot.DoesNotExist:
            return serializers.ValidationError({"message": "Close Floot does not exist."})

        old_fill_credit_amount = instance.fill_credit

        if old_fill_credit_amount < 0:
            close_floot.total_fill -= old_fill_credit_amount
            close_floot.result -= old_fill_credit_amount
            if new_fill_credit_amount < 0:
                close_floot.total_fill += new_fill_credit_amount
                close_floot.result += new_fill_credit_amount
                close_floot.save()
            elif new_fill_credit_amount > 0:
                close_floot.total_credit += new_fill_credit_amount
                close_floot.result += new_fill_credit_amount
                close_floot.save()
            else:
                return serializers.ValidationError({"message": "Fill Credit amount cannot be zero."})

        elif old_fill_credit_amount > 0:
            close_floot.total_credit -= old_fill_credit_amount
            close_floot.result -= old_fill_credit_amount
            if new_fill_credit_amount < 0:
                close_floot.total_fill += new_fill_credit_amount
                close_floot.result += new_fill_credit_amount
                close_floot.save()
            elif new_fill_credit_amount > 0:
                close_floot.total_credit += new_fill_credit_amount
                close_floot.result += new_fill_credit_amount
                close_floot.save()
            else:
                return serializers.ValidationError({"message": "Fill Credit amount cannot be zero."})

        instance.fill_credit = new_fill_credit_amount
        instance.action_time = new_action_time
        instance.updated_at = timezone.now() + timedelta(hours=4)
        instance.save()

        try:
            table_result = TableResult.objects.get(
                table=table_id, game_day_id=game_day_id
            )
        except TableResult.DoesNotExist:
            raise serializers.ValidationError({"message": "Table Result does not exist."})

        table_result.result -= old_fill_credit_amount
        table_result.result += new_fill_credit_amount
        table_result.save()

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
