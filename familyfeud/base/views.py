from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from asgiref.sync import async_to_sync
from django.db.models import Q
from .models import Question, Game, Answer, GameStatus
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers


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

def send_current_game_state(game_state):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'displayanswer_base',
        {
            'type': 'send_state',
            'state': game_state
        }
    )

def get_current_game_state_as_dict():
    current_game_status = json.loads(serializers.serialize("json", [getCurrentGameStatus()]))
    return current_game_status[0]['fields']

@csrf_exempt
def createNewGame(request):
    """ Creates a new 'GameStatus'. Supply the id of the 'game' you wish to use using 'game' as form data."""
    if request.method == 'POST':
        try:
            current_game = Game.objects.get(pk=request.POST['game'])
            new_game_status = GameStatus.objects.create(current_game=current_game)
            first_question = Question.objects.filter(game=current_game).order_by('question_order')[0] # Get the first question in the seleced game
            new_game_status.current_question = first_question
            new_game_status.save()
        except Exception as e:
            print(e)
            return JsonResponse({'isSucessful': False})
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSucessful': True, 'gameId': new_game_status.pk})

@csrf_exempt
def nextQuestion(request):
    """ Finds the next question and makes it the current_question. Also resets values such as question_total and total_wrong. """
    if request.method == 'POST':
        try:
            current_game_status = getCurrentGameStatus()
            order = current_game_status.current_question.question_order
            next_question = Question.objects.filter(Q(game=current_game_status.current_game) & Q(question_order__gt=order)).order_by('question_order')
            if next_question.count() == 0:
                return JsonResponse({'isSucessful': True, 'text': 'Last Question reached.'})
            current_game_status.current_question = next_question[0]
            current_game_status.displayed_answers = '{"displayed":[]}'
            current_game_status.question_total = 0
            current_game_status.question_total_wrong = 0
            current_game_status.display_logo = True
            current_game_status.save()
        except Exception as e:
            print(e)
            return JsonResponse({'isSucessful': False})
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSucessful': True, 'orderId': next_question[0].question_text})

@csrf_exempt
def displayAnswer(request):
    """ Pass in an 'answerId' as formdata to add it to the 'currently_displayed' array and add it's value to the question_total. """
    if request.method == 'POST':
        try:
            answer_id = request.POST['answerId']
            current_game_status = getCurrentGameStatus()

            answer_to_display = Answer.objects.filter(pk=answer_id)  # Get the answer associated the id
            if not answer_to_display:  # No answer with that ID found
                return JsonResponse({'isSucessful': False, 'errorText': 'Answer does not exist.'})
            if answer_to_display[0].question_id != current_game_status.current_question.pk:  # Answer is not for the current question.
                return JsonResponse({'isSucessful': False, 'errorText': 'That answer does not belong to the current question.'})

            currently_displayed = json.loads(current_game_status.displayed_answers)['displayed']
            if answer_id not in currently_displayed:  # Append if answer is not already displayed
                currently_displayed.append(answer_id)
                current_game_status.question_total += answer_to_display[0].point_value
                current_game_status.new_displayed_answers.add(answer_to_display[0])
            updated_json = json.dumps({'displayed': currently_displayed})
            current_game_status.displayed_answers = updated_json
            current_game_status.save()      
        except Exception as e:
            print(e)
            return JsonResponse({'isSucessful': False})
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSucessful': True, 'currentlyDisplayed': currently_displayed})

@csrf_exempt
def addWrong(request):
    """ Adds a single one to the current question_total_wrong, setting it back to 0 if it reaches 4. """
    if request.method == 'POST':
        current_game_status = getCurrentGameStatus()
        current_game_status.question_total_wrong += 1
        if current_game_status.question_total_wrong >= 4:
            current_game_status.question_total_wrong = 0
        current_game_status.save()
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSucessful': True, 'currentWrong': current_game_status.question_total_wrong})

@csrf_exempt
def awardPoints(request):
    """ Award points of question_total to a given team. Pass in 'teamToReward' as either 'one' or 'two' to award the points. """
    if request.method == 'POST':
        team_to_reward = request.POST['teamToReward']
        if team_to_reward != 'one' and team_to_reward != 'two':
            print(team_to_reward)
            return JsonResponse({'isSucessful': False, 'errorText': 'Please pick team "one" or team "two"'})
        current_game_status = getCurrentGameStatus()
        if team_to_reward == 'one':
            current_game_status.team_1_score += current_game_status.question_total
        elif team_to_reward == 'two':
            current_game_status.team_2_score += current_game_status.question_total
        current_game_status.question_total = 0
        current_game_status.save()
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSucessful': True, 'team_1_score': current_game_status.team_1_score, 'team_2_score': current_game_status.team_2_score})

@csrf_exempt
def revealBoard(request):
    if request.method == 'POST':
        current_game_status = getCurrentGameStatus()
        current_game_status.display_logo = False
        current_game_status.save()
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSucessful': True})

@csrf_exempt
def hideBoard(request):
    if request.method == 'POST':
        current_game_status = getCurrentGameStatus()
        current_game_status.display_logo = True
        current_game_status.save()
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSucessful': True})