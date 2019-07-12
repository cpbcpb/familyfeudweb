from django.shortcuts import render
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.db.models import Q
from .models import Question, QuestionSet, Answer
from django.views.decorators.csrf import csrf_exempt
import base.data_handler as data_handler
import json

# Basic functions
def setJsonResponse(data_response):
    if data_response['isSuccessful']:
        return JsonResponse({'isSuccessful': True, 'state': data_handler.get_current_game_state_as_dict()})
    else:
        if 'error' in data_response:
            return JsonResponse({'isSuccessful': False, 'error_message': data_response['error']})
        else:
            return JsonResponse({'isSuccessful': False})



def game(request):
    game_state = data_handler.get_current_game_state_as_dict()

    return render(request, 'base/game_board.html', {
        'state': mark_safe(json.dumps(game_state))
    })



def getCurrentGameStatus():
    if len(GameStatus.objects.filter().order_by('-create_date')) == 0:
        return {}
    return GameStatus.objects.filter().order_by('-create_date')[0]
# Here we begin the actual views / routes

def questions(request):
    return render(request, 'base/questions.html')

def adminquestions(request): 
    """ Display the admin dashboard """
    question_set_list = list(QuestionSet.objects.values())
    game_state = data_handler.get_current_game_state_as_dict()
    current_game_status = data_handler.getCurrentGameStatus()
    fast_money_answers = {}
    if not game_state['no_active_game']:
        fast_money_questions = list(Question.objects.filter(Q(game=current_game_status.current_game) & Q(is_fast_money=True)).values().order_by('question_order'))
        for question in fast_money_questions:
            fast_money_answers[question['id']] = list(Answer.objects.filter(question_id=question['id']).order_by('-point_value').values())

    return render(request, 'base/admin-questions.html', {
        'question_sets': mark_safe(json.dumps(question_set_list)),
        'state': mark_safe(json.dumps(game_state)),
        'fast_money_answers': mark_safe(json.dumps(fast_money_answers))
    })

@csrf_exempt
def createNewGame(request):
    """ Creates a new 'GameStatus'. Supply the id of the 'game' you wish to use using 'game' as form data."""
    if request.method == 'POST':
        data_response = data_handler.createNewGame(request.POST['game'])
        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def nextQuestion(request):
    """ Finds the next question and makes it the current_question. Also resets values such as question_total and total_wrong. """
    if request.method == 'POST':
        data_response = data_handler.setNextQuestion()
        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def displayAnswer(request):
    """ Pass in an 'answerId' as formdata to add it to the 'currently_displayed' array and add it's value to the question_total. """
    if request.method == 'POST':
        answer_id = request.POST['answerId']
        data_response = data_handler.displayAnswer(answer_id)
        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def hideAnswer(request):
    """ Pass in an 'answerId' as formdata to add it to the 'currently_displayed' array and add it's value to the question_total. """
    if request.method == 'POST':
        answer_id = request.POST['answerId']
        data_response = data_handler.hideAnswer(answer_id)
        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def addWrong(request):
    """ Adds a single one to the current question_total_wrong, setting it back to 0 if it reaches 4. """
    if request.method == 'POST':
        data_response = data_handler.addToWrongAnswerCount()

        if data_response['isSuccessful']:
            game_state = data_handler.get_current_game_state_as_dict()
            game_state['show_total_wrong'] = True
            data_handler.send_current_game_state(game_state)
        
        return setJsonResponse(data_response)

@csrf_exempt
def awardPoints(request):
    """ Award points of question_total to a given team. Pass in 'teamToReward' as either 'one' or 'two' to award the points. """
    if request.method == 'POST':
        team_to_reward = request.POST['teamToReward']
        data_response = data_handler.awardPoints(team_to_reward)

        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def editPoints(request):
    """ Used to manually update points. """
    if request.method == 'POST':
        team_one_points = request.POST['teamOnePoints']
        team_two_points = request.POST['teamTwoPoints']
        data_response = data_handler.editTeamPoints(team_one_points, team_two_points)
        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def revealBoard(request):
    if request.method == 'POST':
        data_response = data_handler.toggleLogo(display_logo=False)
        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def hideBoard(request):
    if request.method == 'POST':
        data_response = data_handler.toggleLogo(display_logo=True)
        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def showSingleX(request):
    if request.method == 'POST':
        game_state = data_handler.get_current_game_state_as_dict()
        game_state['show_single_x'] = True
        data_handler.send_current_game_state(game_state)
        return JsonResponse({'isSuccessful': True})

@csrf_exempt
def editTotalWrong(request):
    """ Manually updates the total wrong for the current question. """
    if request.method == 'POST':
        total_wrong = request.POST['totalWrong']
        show_buzzer = request.POST['showBuzzer']

        data_response = data_handler.editTotalWrong(total_wrong)

        if data_response['isSuccessful']:
            game_state = data_handler.get_current_game_state_as_dict()
            if show_buzzer == '1':
                game_state['show_total_wrong'] = True
            data_handler.send_current_game_state(game_state)

        return setJsonResponse(data_response)

@csrf_exempt
def answerFastMoney(request):
    """ Inserts the text of a fast money answer. """
    if request.method == 'POST':
        answer_text = request.POST['answer']
        question = request.POST['question']
        player = request.POST['player']

        data_response = data_handler.updateFastMoneyAnswer(answer_text, question, player)

        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def assignPointValue(request):
    """ Assigns a point value to a given fast money answer using the answer ID . """
    if request.method == 'POST':
        answer_id = request.POST['answer_id']
        question = request.POST['question']
        player = request.POST['player']
        
        data_response = data_handler.assignFastMoneyAnswerPointValue(answer_id, question, player)

        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def toggleFastMoneyAnswer(request):
    """ Assigns a point value to a given fast money answer using the answer ID . """
    if request.method == 'POST':
        question_id = request.POST['question']
        player = request.POST['player']
        display_it = request.POST['displayIt']

        data_response = data_handler.toggleFastMoneyAnswerDisplay(question_id, player, display_it)

        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def toggleFastMoneyValue(request):
    """ Assigns a point value to a given fast money answer using the answer ID . """
    if request.method == 'POST':
        question_id = request.POST['question']
        player = request.POST['player']
        display_it = request.POST['displayIt']

        data_response = data_handler.toggleFastMoneyValueDisplay(question_id, player, display_it)
 
        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def setTimer(request):
    """ Assigns a point value to a given fast money answer using the answer ID . """
    if request.method == 'POST':
        timer = request.POST['timer']

        data_response = data_handler.updateTimer(timer)

        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)

@csrf_exempt
def toggleTimer(request):
    """ Assigns a point value to a given fast money answer using the answer ID . """
    if request.method == 'POST':
        startTimer = request.POST['startTimer']
        try:
            game_state = data_handler.get_current_game_state_as_dict()
            if startTimer == '1':
                game_state['fast_money']['start_timer'] = True
                game_state['fast_money']['stop_timer'] = False
            else:
                game_state['fast_money']['start_timer'] = False
                game_state['fast_money']['stop_timer'] = True
        except Exception as e: 
            print(e)
            return JsonResponse({'isSuccessful': False})
        data_handler.send_current_game_state(game_state)
        return JsonResponse({'isSuccessful': True, 'state': data_handler.get_current_game_state_as_dict()})

@csrf_exempt
def toggleFastMoney(request):
    """ Assigns a point value to a given fast money answer using the answer ID . """
    if request.method == 'POST':
        start_fast_money = request.POST['startFastMoney']
        
        data_response = data_handler.toggleFastMoney(start_fast_money)

        if data_response['isSuccessful']:
            data_handler.send_current_game_state(data_handler.get_current_game_state_as_dict())
        return setJsonResponse(data_response)