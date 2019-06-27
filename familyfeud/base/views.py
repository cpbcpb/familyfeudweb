from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from asgiref.sync import async_to_sync
from django.db.models import Q
from .models import Question, Game, Answer, GameStatus
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt

import json

def getCurrentGameStatus():
    return GameStatus.objects.filter().order_by('-create_date')[0]

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
    game_list = list(Game.objects.values())
    # game_list = []
    # for game in game_query:
    #     game_list.append({'id': game.id, 'name': game.friendly_name})
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
        'answers': mark_safe(json.dumps(answers)),
        'games': mark_safe(json.dumps(game_list))
    })

def gamelist(request):
    gamelist = list(Game.objects.values())
    return render(request, 'base/game-list.html', {
        'games': mark_safe(json.dumps(gamelist))
    })

def addWrong(request):
    if request.method == 'POST':
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            '{}'.format('displayanswer_base'),
            {
                'type': 'add_wrong',
                'action': 'addWrong'
            }
        )
        return JsonResponse({'isSucessful': True})

# This creates an empty game status in the database
@csrf_exempt
def createNewGame(request):
    if request.method == 'POST':
        try:
            currentGame = Game.objects.get(pk=request.POST['game'])
            newGameStatus = GameStatus.objects.create(current_game=currentGame)
            currentQuestion = Question.objects.filter(game=currentGame).order_by('question_order')[0] # Get the first question in the seleced game
            newGameStatus.current_question = currentQuestion
            newGameStatus.save()
        except Exception as e:
            print(e)
            return JsonResponse({'isSucessful': False})
        return JsonResponse({'isSucessful': True, 'gameId': newGameStatus.pk})

@csrf_exempt
def nextQuestion(request):
    if request.method == 'POST':
        try:
            currentGameStatus = getCurrentGameStatus()
            order = currentGameStatus.current_question.question_order
            nextQuestion = Question.objects.filter(Q(game=currentGameStatus.current_game) & Q(question_order__gt=order)).order_by('question_order')
            if nextQuestion.count() == 0:
                return JsonResponse({'isSucessful': True, 'text': 'Last Question reached.'})
            currentGameStatus.current_question = nextQuestion[0]
            currentGameStatus.save()
        except Exception as e:
            print(e)
            return JsonResponse({'isSucessful': False})
        return JsonResponse({'isSucessful': True, 'orderId': nextQuestion[0].question_text})

@csrf_exempt
def displayAnswer():
    pass