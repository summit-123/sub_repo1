from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Avg
from django.http import HttpResponse
from django.utils import timezone
from django.core.serializers import serialize
from .serializers import DeckSerializer, FlashcardSerializer
from .models import Deck, Flashcard
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from datetime import timedelta, date
from .utils.spaced_repetition import update_review_schedule
from fuzzywuzzy import fuzz, process
import json
import csv

# THIS IS A COMMENT
def deck_list(request):
    # refer to get_deck API endpoint
    decks = Deck.objects.all()
    initial_data = {
        'decks': serialize('json', decks),
        'user': {
            'id': request.user.id,
            'username': request.user.username,
        } if request.user.is_authenticated else None,
    }
    return render(request, 'deck_list.html', {'initial_data': initial_data})

def deck_detail(request, deck_id):
    deck = Deck.objects.get(id=deck_id)
    initial_data = {
        'deck': serialize('json', [deck])[1:-1],  # Remove outer brackets
        'user': {
            'id': request.user.id,
            'username': request.user.username,
        } if request.user.is_authenticated else None,
    }
    return render(request, 'deck_detail.html', {'initial_data': initial_data})



def index(request):
    initial_data = {
        'decks': serialize('json', Deck.objects.all()),
        'user': {
            'id': request.user.id,
            'username': request.user.username,
        } if request.user.is_authenticated else None,
    }
    return render(request, 'index.html', {'initial_data': initial_data})


############################### VIEWSETS #######################################
class DeckViewSet(viewsets.ModelViewSet):
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer

class FlashcardViewSet(viewsets.ModelViewSet):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer

    def get_queryset(self):
        queryset = Flashcard.objects.all()
        deck_id = self.request.query_params.get('deck_id', None)
        if deck_id is not None:
            queryset = queryset.filter(deck_id=deck_id)
        return queryset
############################### API endpoints #######################################
@api_view(['GET'])
def get_data(request):
    # Sample data to return
    data = {
        "message": "Hello from Django API",
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
        ],
    }
    return Response(data)

# @api_view(['GET'])
# def get_deck(request, id):
# # def get_decks(request):    
#     deck = Deck.objects.get(id=id)
#     # decks = Deck.objects.all()
#     serializer = DeckSerializer(deck)
#     # serializer = DeckSerializer(decks, many=True)
#     data = serializer.data
#     # Add any build-time specific data
#     data['lastUpdated'] = deck.updated_at.isoformat()
#     # return Response(serializer.data)  
#     return Response(data) 

@api_view(['GET'])
def get_due_cards(request):
    today = timezone.now().date()
    due_cards = Flashcard.objects.filter(next_review__lte=today)
    return Response([{'id': card.id, 'front': card.front, 'back': card.back}])

# v1.B.1 --> endpoint for the Fuzzy Search Functionality
@api_view(['GET'])
def search_flashcards(request):
    query = request.GET.get('query', '')
    # results = search_flashcards_pg(query)  # Use the [POSTGRES_SQL] selected method
    # return Response([{'id': card.id, 'front': card.front, 'back': card.back} for card in results])
    results = search_flashcards_fuzzy(query)
    return Response([{'id': card.id, 'front': card.front, 'back': card.back} for card, _ in results])

# v1.B.4
@api_view(['POST'])
def update_review(request, pk):
    flashcard = get_object_or_404(Flashcard, pk=pk)
    quality = request.data.get('quality', 0)
    update_review_schedule(flashcard, quality)      
    # recall_success = request.data.get('success', False)
    # update_review_schedule(flashcard, recall_success)
    return Response({'status': 'success', 'next_review': flashcard.next_review})

@api_view(['POST'])
def import_deck(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file provided'}, status=400)

    if file.name.endswith('.json'):
        data = json.load(file)
        deck = Deck.objects.create(name=data['name'])
        for card_data in data['cards']:
            Flashcard.objects.create(deck=deck, front=card_data['front'], back=card_data['back'])
    elif file.name.endswith('.csv'):
        deck = Deck.objects.create(name=file.name[:-4])
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        for row in reader:
            if len(row) >= 2:
                Flashcard.objects.create(deck=deck, front=row[0], back=row[1])
    else:
        return Response({'error': 'Unsupported file format'}, status=400)

    return Response({'message': 'Deck imported successfully'})

@api_view(['GET'])
def export_deck(request, deck_id):
    try:
        deck = Deck.objects.get(id=deck_id)
    except Deck.DoesNotExist:
        return Response({'error': 'Deck not found'}, status=404)

    format = request.GET.get('format', 'json')

    if format == 'json':
        data = {
            'name': deck.name,
            'cards': list(deck.flashcards.values('front', 'back'))
        }
        response = HttpResponse(json.dumps(data), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{deck.name}.json"'
    elif format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{deck.name}.csv"'
        writer = csv.writer(response)
        for card in deck.flashcards.all():
            writer.writerow([card.front, card.back])
    else:
        return Response({'error': 'Unsupported export format'}, status=400)

    return response


@api_view(['GET'])
def deck_statistics(request, deck_id):
    try:
        deck = Deck.objects.get(id=deck_id)
    except Deck.DoesNotExist:
        return Response({'error': 'Deck not found'}, status=404)

    total_cards = deck.flashcards.count()
    cards_due = deck.flashcards.filter(next_review__lte=timezone.now().date()).count()
    avg_interval = deck.flashcards.aggregate(Avg('interval'))['interval__avg']

    return Response({
        'total_cards': total_cards,
        'cards_due': cards_due,
        'average_interval': avg_interval or 0
    })

############################### util functions #######################################
# non-API views
# v1.A.1 --> Fuzzy Search functionality
def search_flashcards_fuzzy(query, threshold=60): # Modified
    cards = Flashcard.objects.all()
    results = []
    for card in cards:
        relevance = fuzz.partial_ratio(query, f"{card.front} {card.back}")
        if relevance >= threshold:          # AGGREGATED CONDITIONAL APPENDING
            results.append((card, relevance))
    return sorted(results, key=lambda x: x[1], reverse=True)




# v1.B.2
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)



# v1.B.6
def update_review_schedule(flashcard, recall_success):
    if recall_success:
        flashcard.success_count += 1
    else:
        flashcard.success_count = max(flashcard.success_count - 1, 0)

    # Adjust interval using Fibonacci sequence
    flashcard.interval = fibonacci(flashcard.success_count)
    flashcard.last_reviewed = date.today()
    flashcard.next_review = date.today() + timedelta(days=flashcard.interval)
    flashcard.save()
