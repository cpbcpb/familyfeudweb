from asgiref.sync import async_to_sync
from django.db.models import Q
from .models import Question, QuestionSet, Answer, GameStatus, FastMoneyAnswer
from channels.layers import get_channel_layer
from django.forms.models import model_to_dict


def getCurrentGameStatus():
    if len(GameStatus.objects.filter().order_by('-create_date')) == 0:
        return {}
    return GameStatus.objects.filter().order_by('-create_date')[0]

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
            'no_active_game': True,
        }
    current_answers = list(Answer.objects.filter(question_id=current_game_status.current_question_id).order_by('-point_value').values())
    displayed_answers = list(current_game_status.displayed_answers.values())

    for answer in current_answers:
        if answer in displayed_answers:
            answer['currently_displayed'] = True
        else:
            answer['currently_displayed'] = False

    fast_money_questions = Question.objects.filter(Q(game=current_game_status.current_game_id) & Q(is_fast_money=True))
    questions = []
    for question in fast_money_questions:
        fast_money_question = {
            'text': question.question_text,
            'order': question.question_order,
            'id': question.pk,
            'player_1_answer': FastMoneyAnswer.objects.filter(Q(game_status=current_game_status) & Q(question=question) & Q(player=1)).values()[0],
            'player_2_answer': FastMoneyAnswer.objects.filter(Q(game_status=current_game_status) & Q(question=question) & Q(player=2)).values()[0]
        }
        questions.append(fast_money_question)

    return {
        'team_1_score': current_game_status.team_1_score,
        'team_2_score': current_game_status.team_2_score,
        'question_total': current_game_status.question_total,
        'total_wrong': current_game_status.question_total_wrong,
        'current_game_id': current_game_status.current_game_id,
        'current_question_id': current_game_status.current_question_id,
        'current_question': model_to_dict(current_game_status.current_question),
        'last_question': model_to_dict(current_game_status.last_question),
        'create_date': current_game_status.create_date.__str__(),
        'display_logo': current_game_status.display_logo,
        'current_answers': current_answers,
        'points_awarded': current_game_status.points_awarded,
        'is_fast_money': current_game_status.is_fast_money,
        'fast_money': {
            'player_1_score': current_game_status.player_1_score,
            'player_2_score': current_game_status.player_2_score,
            'timer': current_game_status.timer,
            'display_timer': current_game_status.display_timer,
            'start_timer': False,
            'stop_timer': False,
            'questions': questions
        },
        'show_single_x': False,
        'show_total_wrong': False,
        'no_active_game': False,
    }

def sumAnswerTotals(answers):
    total = 0
    for answer in answers:
        total += answer['point_value']
    return total

def createNewGame(question_set):
    try: 
        current_game = QuestionSet.objects.get(pk=question_set)
        new_game_status = GameStatus.objects.create(current_game=current_game)
        first_question = Question.objects.filter(Q(game=current_game) & Q(is_fast_money=False)).order_by('question_order')[0] # Get the first question in the seleced game
        last_question = Question.objects.filter(Q(game=current_game) & Q(is_fast_money=False)).order_by('-question_order')[0]
        new_game_status.current_question = first_question
        new_game_status.last_question = last_question
        new_game_status.save()
        fast_money_questions = Question.objects.filter(Q(game=current_game) & Q(is_fast_money=True))
        for question in fast_money_questions:
            # We create empty answers for both player 1 and 2 for fast money so the objects exist in the state object
            player_1_answer = FastMoneyAnswer.objects.create(game_status=new_game_status, question=question, player=1)
            player_2_answer = FastMoneyAnswer.objects.create(game_status=new_game_status, question=question, player=2)
            player_1_answer.save()
            player_2_answer.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}

def setNextQuestion():
    try:
        current_game_status = getCurrentGameStatus()
        order = current_game_status.current_question.question_order
        next_question = Question.objects.filter(Q(game=current_game_status.current_game) & Q(is_fast_money=False) & Q(question_order__gt=order)).order_by('question_order')
        if next_question.count() == 0:
            return {'isSuccessful': False, 'error': 'Last Question reached.'}
        current_game_status.current_question = next_question[0]
        current_game_status.displayed_answers.clear()
        current_game_status.question_total = 0
        current_game_status.question_total_wrong = 0
        current_game_status.points_awarded = False
        current_game_status.display_logo = True
        current_game_status.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}

def displayAnswer(answer_id):
    try:
        current_game_status = getCurrentGameStatus()

        answer_to_display = Answer.objects.filter(pk=answer_id)  # Get the answer associated the id
        if not answer_to_display:  # No answer with that ID found
            return {'isSuccessful': False, 'error': 'Answer does not exist.'}
        if answer_to_display[0].question_id != current_game_status.current_question.pk:  # Answer is not for the current question.
            return {'isSuccessful': False, 'error': 'That answer does not belong to the current question.'}

        current_game_status.displayed_answers.add(answer_to_display[0])
        current_game_status.save()
        if not current_game_status.points_awarded:
            currently_displayed = list(current_game_status.displayed_answers.values())
            current_game_status.question_total = sumAnswerTotals(currently_displayed)
            current_game_status.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}

def hideAnswer(answer_id):
    try:
        current_game_status = getCurrentGameStatus()

        answer_to_hide = Answer.objects.filter(Q(pk=answer_id) & Q(gamestatus__pk=current_game_status.pk))
        if not answer_to_hide:  # No answer with that ID found
            return {'isSuccessful': False, 'error': 'Answer is not being displayed.'}
        current_game_status.displayed_answers.remove(answer_to_hide[0])
        current_game_status.save()

        if not current_game_status.points_awarded:
            currently_displayed = list(current_game_status.displayed_answers.values())
            current_game_status.question_total = sumAnswerTotals(currently_displayed)
            current_game_status.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}

def addToWrongAnswerCount():
    current_game_status = getCurrentGameStatus()
    current_game_status.question_total_wrong += 1
    if current_game_status.question_total_wrong >= 4:
        current_game_status.question_total_wrong = 0
    current_game_status.save()
    return {'isSuccessful': True}

def awardPoints(team_to_reward):
    if team_to_reward != 'one' and team_to_reward != 'two':
        return {'isSuccessful': False, 'error': 'Please pick team "one" or team "two"'}
    current_game_status = getCurrentGameStatus()
    if team_to_reward == 'one':
        current_game_status.team_1_score += current_game_status.question_total
    elif team_to_reward == 'two':
        current_game_status.team_2_score += current_game_status.question_total
    current_game_status.question_total = 0
    current_game_status.points_awarded = True
    current_game_status.save()
    return {'isSuccessful': True}

def editTeamPoints(team_one_points, team_two_points):
    current_game_status = getCurrentGameStatus()
    current_game_status.team_1_score = team_one_points
    current_game_status.team_2_score = team_two_points
    current_game_status.save()
    return {'isSuccessful': True}

def toggleLogo(display_logo):
    current_game_status = getCurrentGameStatus()
    current_game_status.display_logo = display_logo
    current_game_status.save()
    return {'isSuccessful': True}
    
def editTotalWrong(total_wrong):
    current_game_status = getCurrentGameStatus()
    current_game_status.question_total_wrong = total_wrong
    current_game_status.save()
    return {'isSuccessful': True}

def updateFastMoneyAnswer(answer_text, question, player):
    current_game_status = getCurrentGameStatus()
    question = Question.objects.get(pk=question)
    fast_money_answer = FastMoneyAnswer.objects.filter(Q(question=question) & Q(game_status=current_game_status) & Q(player=player))[0]
    fast_money_answer.answer_text = answer_text
    fast_money_answer.save()
    return {'isSuccessful': True}

def assignFastMoneyAnswerPointValue(answer_id, question, player):
    try:
        current_game_status = getCurrentGameStatus()
        question = Question.objects.get(pk=question)
        fast_money_answer = FastMoneyAnswer.objects.filter(Q(question=question) & Q(game_status=current_game_status) & Q(player=player))[0]
        if int(answer_id) > 0:
            answer = Answer.objects.get(pk=answer_id)
            fast_money_answer.point_value = answer.point_value
        else:
            fast_money_answer.point_value = 0
        fast_money_answer.answer_id = answer_id
        fast_money_answer.save()
        fast_money_answers = FastMoneyAnswer.objects.filter(Q(game_status=current_game_status) & Q(player=player))
        player_total = 0
        for answer in fast_money_answers:
            player_total += answer.point_value
        if int(player) == 1:
            current_game_status.player_1_score = player_total
        elif int(player) == 2:
            current_game_status.player_2_score = player_total
        current_game_status.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}


def toggleFastMoneyAnswerDisplay(question_id, player, display_it):
    try:
        current_game_status = getCurrentGameStatus()
        question = Question.objects.get(pk=question_id)
        fast_money_answer = FastMoneyAnswer.objects.filter(Q(question=question) & Q(game_status=current_game_status) & Q(player=player))[0]
        if display_it == '1':
            fast_money_answer.display_answer = True
        else:
            fast_money_answer.display_answer = False
        fast_money_answer.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}

def toggleFastMoneyValueDisplay(question_id, player, display_it):
    try:
        current_game_status = getCurrentGameStatus()
        question = Question.objects.get(pk=question_id)
        fast_money_answer = FastMoneyAnswer.objects.filter(Q(question=question) & Q(game_status=current_game_status) & Q(player=player))[0]
        if display_it == '1':
            fast_money_answer.display_value = True
        else:
            fast_money_answer.display_value = False
        fast_money_answer.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}

def updateTimer(timer_value):
    try:
        current_game_status = getCurrentGameStatus()
        current_game_status.timer = timer_value
        current_game_status.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}

def toggleDisplayTimer(display_timer):
    try:
        currentGameStatus = getCurrentGameStatus()
        if display_timer == '1':
            currentGameStatus.display_timer = True
        else:
            currentGameStatus.display_timer = False
        currentGameStatus.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}

def toggleFastMoney(start_fast_money):
    try:
        currentGameStatus = getCurrentGameStatus()
        if start_fast_money == '1':
            currentGameStatus.is_fast_money = True
            currentGameStatus.display_logo = True
        else:
            currentGameStatus.is_fast_money = False
        currentGameStatus.save()
    except Exception as e:
        print(e)
        return {'isSuccessful': False}
    return {'isSuccessful': True}