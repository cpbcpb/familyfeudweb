# Generated by Django 2.2.2 on 2019-07-05 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_question_is_fast_money'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamestatus',
            name='player_1_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='gamestatus',
            name='player_2_score',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='FastMoneyAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(default='', max_length=500)),
                ('point_value', models.IntegerField(default=0)),
                ('display_answer', models.BooleanField(default=False)),
                ('display_value', models.BooleanField(default=False)),
                ('player', models.IntegerField(default=0)),
                ('game_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.GameStatus')),
                ('question_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Question')),
            ],
        ),
    ]
