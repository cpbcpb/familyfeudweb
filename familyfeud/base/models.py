from django.db import models
from django.utils.timezone import now

# Create your models here.
class QuestionSet(models.Model):
    friendly_name = models.CharField(max_length=500)

    def __str__(self):
        return self.friendly_name

class Question(models.Model):
    question_text = models.CharField(max_length=500)
    game = models.ForeignKey(QuestionSet, on_delete=models.CASCADE)
    question_order = models.IntegerField(default=0)
    is_fast_money = models.BooleanField(default=False)
    score_multiplier = models.IntegerField(default=1)
    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=500)
    point_value = models.IntegerField(default=0)

    def __str__(self):
        return self.answer_text

class GameStatus(models.Model):
    current_game = models.ForeignKey(QuestionSet, on_delete=models.CASCADE, null=True, blank=True)
    team_1_score = models.IntegerField(default=0)
    team_2_score = models.IntegerField(default=0)
    team_1_name = models.CharField(default='', max_length=500)
    team_2_name = models.CharField(default='', max_length=500)
    cooperative_fm = models.BooleanField(default=True)
    current_fm_player = models.IntegerField(default=1)
    current_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    question_total = models.IntegerField(default=0)
    question_total_wrong = models.IntegerField(default=0)
    display_logo = models.BooleanField(default=True)
    display_picture = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=now)
    points_awarded = models.BooleanField(default=False)
    displayed_answers = models.ManyToManyField(Answer, blank=True)
    is_fast_money = models.BooleanField(default=False)
    player_1_score = models.IntegerField(default=0)
    player_2_score = models.IntegerField(default=0)
    timer = models.IntegerField(default=25)
    display_timer = models.BooleanField(default=False)
    last_question = models.ForeignKey(Question, related_name='last_question', on_delete=models.CASCADE, null=True, blank=True)
    display_winner_screen = models.BooleanField(default=False)
    winner_name = models.CharField(default='', max_length=200)


class FastMoneyAnswer(models.Model):
    game_status = models.ForeignKey(GameStatus, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(default='', max_length=500)
    point_value = models.IntegerField(default=0)
    answer_id = models.IntegerField(default=0) # We're using an int field instead of Foreign key because this is only used for the Admin Dropdown and may be zero (for incorrect).
    display_answer = models.BooleanField(default=False)
    display_value = models.BooleanField(default=False)
    player = models.IntegerField(default=0)