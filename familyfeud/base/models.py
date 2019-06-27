from django.db import models
from django.utils.timezone import now

# Create your models here.
class Game(models.Model):
    friendly_name = models.CharField(max_length=500)

    def __str__(self):
        return self.friendly_name

class Question(models.Model):
    question_text = models.CharField(max_length=500)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    question_order = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=500)
    point_value = models.IntegerField(default=0)

    def __str__(self):
        return self.answer_text

class GameStatus(models.Model):
    current_game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    team_1_score = models.IntegerField(default=0)
    team_2_score = models.IntegerField(default=0)
    current_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    question_total = models.IntegerField(default=0)
    question_total_wrong = models.IntegerField(default=0)
    displayed_answers = models.CharField(default='{"displayed":[]}', max_length=1000)
    create_date = models.DateTimeField(default=now)