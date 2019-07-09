from django.contrib import admin

from .models import Question, QuestionSet, Answer, GameStatus, FastMoneyAnswer
# Register your models here.


class ChoiceInline(admin.TabularInline):
    model = Answer
    extra = 6


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]


class QuestionSetAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionSet, QuestionSetAdmin)
admin.site.register(Answer)
admin.site.register(GameStatus)
admin.site.register(FastMoneyAnswer)