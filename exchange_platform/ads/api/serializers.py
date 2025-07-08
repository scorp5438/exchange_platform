from rest_framework import serializers

from ..models import Ad, ExchangeProposal, Category


class AdSerializer(serializers.ModelSerializer):
    condition = serializers.ChoiceField(choices=Ad.CONDITION)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'user')
        extra_kwargs = {
            'image_url': {'required': False},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request_method = self.context.get('request').method
        if request_method in ['POST', 'PATCH']:
            data = {k: v for k, v in data.items() if k not in ['user', 'created_at']}
            return {
                'message': 'Ad created successfully' if request_method == 'POST' else 'Ad updated successfully',
                'data': data,
            }
        return data

class ExchangeProposalSerializer(serializers.ModelSerializer):
    ad_sender = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())
    ad_receiver = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())
    status = serializers.ChoiceField(
        choices=ExchangeProposal.STATUSES,
        default='ожидает',
        required=False
    )

    class Meta:
        model = ExchangeProposal
        fields = '__all__'
        read_only_fields = ('id', 'ad_sender', 'ad_receiver', 'created_at')
        extra_kwargs = {
            'comment': {'required': False}
        }

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
