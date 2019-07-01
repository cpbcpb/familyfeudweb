from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from asgiref.sync import async_to_sync
from django.db.models import Q
from .models import Question, QuestionSet, Answer, GameStatus
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict


import json

def getCurrentGameStatus():
    if len(GameStatus.objects.filter().order_by('-create_date')) == 0:
        return {}
    return GameStatus.objects.filter().order_by('-create_date')[0]

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
    """ Display the admin dashboard """
    question_set_list = list(QuestionSet.objects.values())
    game_state = get_current_game_state_as_dict()

    return render(request, 'base/admin-questions.html', {
        'question_sets': mark_safe(json.dumps(question_set_list)),
        'state': mark_safe(json.dumps(game_state))
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
    current_game_status = getCurrentGameStatus()
    if current_game_status == {}:
        return {
            'team_1_score': 0,
            'team_2_score': 0,
            'question_total': 0,
            'total_wrong': 0,
            'current_game_id': 0,
            'current_question_id': 0,
            'current_question': {},
            'create_date': '',
            'display_logo': False,
            'current_answers': [],
            'show_single_x': False,
            'show_total_wrong': False,
            'no_active_game': True
        }
    current_answers = list(Answer.objects.filter(question_id=current_game_status.current_question_id).order_by('-point_value').values())
    displayed_answers = list(current_game_status.displayed_answers.values())

    for answer in current_answers:
        if answer in displayed_answers:
            answer['currently_displayed'] = True
        else:
            answer['currently_displayed'] = False

    return {
        'team_1_score': current_game_status.team_1_score,
        'team_2_score': current_game_status.team_2_score,
        'question_total': current_game_status.question_total,
        'total_wrong': current_game_status.question_total_wrong,
        'current_game_id': current_game_status.current_game_id,
        'current_question_id': current_game_status.current_question_id,
        'current_question': model_to_dict(Question.objects.get(pk=current_game_status.current_question_id)),
        'create_date': current_game_status.create_date.__str__(),
        'display_logo': current_game_status.display_logo,
        'current_answers': current_answers,
        'show_single_x': False,
        'show_total_wrong': False,
        'no_active_game': False
    }

def sumAnswerTotals(answers):
    total = 0
    for answer in answers:
        total += answer['point_value']
    return total

@csrf_exempt
def createNewGame(request):
    """ Creates a new 'GameStatus'. Supply the id of the 'game' you wish to use using 'game' as form data."""
    if request.method == 'POST':
        try:
            current_game = QuestionSet.objects.get(pk=request.POST['game'])
            new_game_status = GameStatus.objects.create(current_game=current_game)
            first_question = Question.objects.filter(game=current_game).order_by('question_order')[0] # Get the first question in the seleced game
            new_game_status.current_question = first_question
            new_game_status.save()
        except Exception as e:
            print(e)
            return JsonResponse({'isSuccessful': False})
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})

@csrf_exempt
def nextQuestion(request):
    """ Finds the next question and makes it the current_question. Also resets values such as question_total and total_wrong. """
    if request.method == 'POST':
        try:
            current_game_status = getCurrentGameStatus()
            order = current_game_status.current_question.question_order
            next_question = Question.objects.filter(Q(game=current_game_status.current_game) & Q(question_order__gt=order)).order_by('question_order')
            if next_question.count() == 0:
                return JsonResponse({'isSuccessful': False, 'text': 'Last Question reached.'})
            current_game_status.current_question = next_question[0]
            current_game_status.displayed_answers.clear()
            current_game_status.question_total = 0
            current_game_status.question_total_wrong = 0
            current_game_status.display_logo = True
            current_game_status.save()
        except Exception as e:
            print(e)
            return JsonResponse({'isSuccessful': False})
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})

@csrf_exempt
def displayAnswer(request):
    """ Pass in an 'answerId' as formdata to add it to the 'currently_displayed' array and add it's value to the question_total. """
    if request.method == 'POST':
        try:
            answer_id = request.POST['answerId']
            current_game_status = getCurrentGameStatus()

            answer_to_display = Answer.objects.filter(pk=answer_id)  # Get the answer associated the id
            if not answer_to_display:  # No answer with that ID found
                return JsonResponse({'isSuccessful': False, 'errorText': 'Answer does not exist.'})
            if answer_to_display[0].question_id != current_game_status.current_question.pk:  # Answer is not for the current question.
                return JsonResponse({'isSuccessful': False, 'errorText': 'That answer does not belong to the current question.'})

            current_game_status.displayed_answers.add(answer_to_display[0])
            current_game_status.save()

            currently_displayed = list(current_game_status.displayed_answers.values())
            current_game_status.question_total = sumAnswerTotals(currently_displayed)
            current_game_status.save()

        except Exception as e:
            print(e)
            return JsonResponse({'isSuccessful': False})
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})

@csrf_exempt
def hideAnswer(request):
    """ Pass in an 'answerId' as formdata to add it to the 'currently_displayed' array and add it's value to the question_total. """
    if request.method == 'POST':
        try:
            answer_id = request.POST['answerId']
            current_game_status = getCurrentGameStatus()

            answer_to_hide = Answer.objects.filter(Q(pk=answer_id) & Q(gamestatus__pk=current_game_status.pk))
            if not answer_to_hide:  # No answer with that ID found
                return JsonResponse({'isSuccessful': False, 'errorText': 'Answer is not being displayed.'})
        
            current_game_status.displayed_answers.remove(answer_to_hide[0])
            current_game_status.save()

            currently_displayed = list(current_game_status.displayed_answers.values())
            current_game_status.question_total = sumAnswerTotals(currently_displayed)
            current_game_status.save()
        except Exception as e:
            print(e)
            return JsonResponse({'isSuccessful': False})
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})

@csrf_exempt
def addWrong(request):
    """ Adds a single one to the current question_total_wrong, setting it back to 0 if it reaches 4. """
    if request.method == 'POST':
        current_game_status = getCurrentGameStatus()
        current_game_status.question_total_wrong += 1
        if current_game_status.question_total_wrong >= 4:
            current_game_status.question_total_wrong = 0
        current_game_status.save()
        game_state = get_current_game_state_as_dict()
        game_state['show_total_wrong'] = True
        send_current_game_state(game_state)
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})

@csrf_exempt
def awardPoints(request):
    """ Award points of question_total to a given team. Pass in 'teamToReward' as either 'one' or 'two' to award the points. """
    if request.method == 'POST':
        team_to_reward = request.POST['teamToReward']
        if team_to_reward != 'one' and team_to_reward != 'two':
            print(team_to_reward)
            return JsonResponse({'isSuccessful': False, 'errorText': 'Please pick team "one" or team "two"'})
        current_game_status = getCurrentGameStatus()
        if team_to_reward == 'one':
            current_game_status.team_1_score += current_game_status.question_total
        elif team_to_reward == 'two':
            current_game_status.team_2_score += current_game_status.question_total
        current_game_status.question_total = 0
        current_game_status.save()
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})

@csrf_exempt
def editPoints(request):
    """ Used to manually update points. """
    if request.method == 'POST':
        team_one_points = request.POST['teamOnePoints']
        team_two_points = request.POST['teamTwoPoints']

        current_game_status = getCurrentGameStatus()
        current_game_status.team_1_score = team_one_points
        current_game_status.team_2_score = team_two_points
        current_game_status.save()
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})

@csrf_exempt
def revealBoard(request):
    if request.method == 'POST':
        current_game_status = getCurrentGameStatus()
        current_game_status.display_logo = False
        current_game_status.save()
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})

@csrf_exempt
def hideBoard(request):
    if request.method == 'POST':
        current_game_status = getCurrentGameStatus()
        current_game_status.display_logo = True
        current_game_status.save()
        send_current_game_state(get_current_game_state_as_dict())
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})

@csrf_exempt
def showSingleX(request):
    if request.method == 'POST':
        game_state = get_current_game_state_as_dict()
        game_state['show_single_x'] = True
        send_current_game_state(game_state)
        return JsonResponse({'isSuccessful': True})

@csrf_exempt
def editTotalWrong(request):
    """ Used to manually update points. """
    if request.method == 'POST':
        total_wrong = request.POST['totalWrong']
        show_buzzer = request.POST['showBuzzer']
        current_game_status = getCurrentGameStatus()
        current_game_status.question_total_wrong = total_wrong
        current_game_status.save()
        game_state = get_current_game_state_as_dict()
        print(show_buzzer)
        if show_buzzer == '1':
            game_state['show_total_wrong'] = True
        send_current_game_state(game_state)
        return JsonResponse({'isSuccessful': True, 'state': get_current_game_state_as_dict()})