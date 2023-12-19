# serializers.py
from rest_framework import serializers
from .models import Word, Definition
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class DefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Definition
        fields = ['id', 'definition_text', 'definition_status', 'total_votes', 'created_at']


class WordSerializer(serializers.ModelSerializer):
    live_definition = DefinitionSerializer()
    definitions = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = [
            'id',
            'word',
            'live_definition',
            'definitions',
            'positive_votes',
            'negative_votes',
            'total_votes',
            'positive_percentage',
            'negative_percentage',
            'status',
            'created_at',
        ]

    def get_definitions(self, obj):
        # You can include sorting logic here if needed
        definitions = Definition.objects.filter(word=obj).exclude(id=obj.live_definition_id)
        # The actual sorting logic can be based on some external input if necessary
        definitions = definitions.order_by('-total_votes', 'created_at')
        return DefinitionSerializer(definitions, many=True).data