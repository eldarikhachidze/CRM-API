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
            print(game_day_id)
        else:
            game_day_id = game_day_data
            print(game_day_id)


        action_time = validated_data.pop('action_time', None)
        print(action_time)


        if action_time:
            if timezone.is_naive(action_time):
                action_time = timezone.make_aware(action_time, timezone.get_current_timezone())
                print('action time', action_time)
            action_date = action_time.date()
            print('action_date', action_date)

            # Fetch the game day ID
            try:
                game_day_id = GameDayLive.objects.get(date=action_date).id
                print(game_day_id)
            except GameDayLive.DoesNotExist:
                print(f"No game day found for date {action_date}")
        else:
            action_time = timezone.now()
            print(action_time)

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
        fill_credit_id = instance.id
        new_fill_credit = validated_data.get('fill_credit')
        table_id = validated_data.get('table')
        game_day_data = validated_data.get('game_day')
        action_time = validated_data.get('action_time')

        if isinstance(game_day_data, GameDayLive):
            game_day_id = game_day_data.id
        else:
            game_day_id = game_day_data

        if action_time:
            if timezone.is_naive(action_time):
                action_time = timezone.make_aware(action_time, timezone.get_current_timezone())
            action_date = action_time.date()

            # Fetch the game day ID
            try:
                game_day_id = GameDayLive.objects.get(date=action_date).id
                print(game_day_id)
            except GameDayLive.DoesNotExist:
                print(f"No game day found for date {action_date}")
        else:
            action_time = timezone.now()
            print(action_time)

        try:
            table_result = TableResult.objects.get(
            table=table_id, game_day=game_day_id
            )
        except TableResult.DoesNotExist:
            raise serializers.ValidationError({"message": "Table Result does not exist."})

        try:
            old_fill_credit = FillCredit.objects.get(id=fill_credit_id).fill_credit
            print('old_fill_credit', old_fill_credit)
        except FillCredit.DoesNotExist:
            raise serializers.ValidationError({"message": "Fill Credit does not exist."})

        try:
            game_day_instance = GameDayLive.objects.get(id=game_day_id)
            print(game_day_instance)
        except GameDayLive.DoesNotExist:
            raise serializers.ValidationError({"message": "Game Day does not exist."})

        table_result.result -= old_fill_credit
        table_result.result += new_fill_credit
        table_result.save()

        fill_credit_instance = FillCredit.objects.get(id=fill_credit_id)
        print('fill_credit_instance', fill_credit_instance)
        fill_credit_instance.fill_credit = new_fill_credit
        print('fill_credit_instance.fill_credit', fill_credit_instance.fill_credit)
        print('new_fill_credit', new_fill_credit)
        fill_credit_instance.table = table_id
        fill_credit_instance.game_day = game_day_instance
        fill_credit_instance.action_time = action_time
        fill_credit_instance.updated_at = timezone.now()
        fill_credit_instance.save()

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
