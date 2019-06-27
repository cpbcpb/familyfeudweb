from django.contrib import admin

from .models import Question, Game, Answer, GameStatus
# Register your models here.


class ChoiceInline(admin.TabularInline):
    model = Answer
    extra = 6


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]


class GameAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Answer)
admin.site.register(GameStatus)