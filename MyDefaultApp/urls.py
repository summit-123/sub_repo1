from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'decks', views.DeckViewSet)
router.register(r'flashcards', views.FlashcardViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/import-deck/', views.import_deck, name='import_deck'),
    path('api/export-deck/<int:deck_id>/', views.export_deck, name='export_deck'),
    path('api/deck-statistics/<int:deck_id>/', views.deck_statistics, name='deck_statistics'),
    path('api/data/', views.get_data, name='get_data'),
    path('api/flashcards/search/', views.search_flashcards, name='search_flashcards'),
    path('api/flashcards/<int:pk>/review/', views.update_review, name='update_review'),
    path('api/flashcards/due/', views.get_due_cards, name='get_due_cards'),
]
