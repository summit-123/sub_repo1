from rest_framework import serializers
from .models import Deck, Flashcard

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = '__all__'

class DeckSerializer(serializers.ModelSerializer):
    flashcard_count = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = ['id', 'name', 'created_at', 'updated_at', 'flashcard_count']

    def get_flashcard_count(self, obj):
        return obj.flashcards.count()