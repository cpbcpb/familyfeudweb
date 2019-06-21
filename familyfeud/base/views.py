from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

# Create your views here.
def button(request):
    return render(request, 'base/button.html', {})

def helloworld(request):
    return render(request, 'base/helloworld.html', {})

def questions(request):
    answers = [
        {'id': 2, 'text': 'Bedroom', 'value': 17},
        {'id': 1, 'text': 'Bathroom / Shower', 'value': 29},
        {'id': 3, 'text': 'Doctor\'s Office / Hospital', 'value': 15},
        {'id': 4, 'text': 'Nude Beach', 'value': 13},
        {'id': 5, 'text': 'Dressing Room', 'value': 12},
        {'id': 6, 'text': 'Gym', 'value': 9},
        {'id': 7, 'text': 'Spa / Massage Joint', 'value': 5},
        
    ]
    return render(request, 'base/questions.html', {
        'answers': mark_safe(json.dumps(answers))
    })

def adminquestions(request):
    answers = [
        {'id': 2, 'text': 'Bedroom', 'value': 17},
        {'id': 1, 'text': 'Bathroom / Shower', 'value': 29},
        {'id': 3, 'text': 'Doctor\'s Office / Hospital', 'value': 15},
        {'id': 4, 'text': 'Nude Beach', 'value': 13},
        {'id': 5, 'text': 'Dressing Room', 'value': 12},
        {'id': 6, 'text': 'Gym', 'value': 9},
        {'id': 7, 'text': 'Spa / Massage Joint', 'value': 5},
        
    ]
    return render(request, 'base/admin-questions.html', {
        'answers': mark_safe(json.dumps(answers))
    })