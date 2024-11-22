from django.db import models

class Deck(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Flashcard(models.Model):
    deck = models.ForeignKey(Deck, related_name='flashcards', on_delete=models.CASCADE)
    front = models.TextField()
    back = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Fields for scheduling
    interval = models.IntegerField(default=1)  # Review interval in days
    repetitions = models.IntegerField(default=0)  # Number of successful reviews
    last_reviewed = models.DateField(null=True, blank=True) # WAS MODIFIED
    next_review = models.DateField(null=True, blank=True)   # WAS MODIFIED