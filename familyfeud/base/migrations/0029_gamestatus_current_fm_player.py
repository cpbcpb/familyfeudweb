# Generated by Django 2.2.4 on 2019-08-21 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_gamestatus_cooperative_fm'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamestatus',
            name='current_fm_player',
            field=models.IntegerField(default=1),
        ),
    ]