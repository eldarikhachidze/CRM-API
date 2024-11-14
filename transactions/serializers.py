from rest_framework import serializers
from .models import FillCredit
from game_table.models import TableResult


class FillCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = FillCredit
        fields = '__all__'

    def create(self, validated_data):
        table_id = validated_data.pop('table')
        game_day_id = validated_data.pop('game_day')
        fill_credit_amount = validated_data.pop('fill_credit')

        print(f"table_id: {table_id.id}")
        print(f"game_day_id: {game_day_id.id}")
        print(f"fill_credit_amount: {fill_credit_amount}")

        table_result, created = TableResult.objects.get_or_create(
            table=table_id, game_day=game_day_id
        )

        credit_amount = FillCredit.objects.create(
            table=table_id,
            game_day=game_day_id,
            fill_credit=fill_credit_amount
        )

        table_result.result += fill_credit_amount
        table_result.save()

        return credit_amount
