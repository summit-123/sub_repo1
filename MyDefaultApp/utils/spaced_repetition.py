from datetime import date, timedelta

def calculate_next_review(quality: int, repetitions: int, previous_interval: int) -> tuple[int, int]:
    if quality < 2:
        return 1, 0
    
    if repetitions == 0:
        interval = 1
    elif repetitions == 1:
        interval = 6
    else:
        interval = round(previous_interval * 2.5)
    
    return interval, repetitions + 1

def update_review_schedule(flashcard, quality: int):
    interval, repetitions = calculate_next_review(quality, flashcard.repetitions, flashcard.interval)
    flashcard.interval = interval
    flashcard.repetitions = repetitions  # AGGREGATED
    flashcard.last_reviewed = date.today()
    flashcard.next_review = date.today() + timedelta(days=interval)
    flashcard.save()