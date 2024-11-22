from django.core.management.base import BaseCommand
from datetime import date
from MyDefaultApp.models import Flashcard

class Command(BaseCommand):
    help = 'Batch process flashcards due for review'

    def handle(self, *args, **kwargs):
        due_cards = Flashcard.objects.filter(next_review__lte=date.today())
        for card in due_cards:
            # Prompt the user or schedule a review
            print(f"Card due for review: {card.front}")
