# Generated by Django 2.2.2 on 2019-07-01 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20190701_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamestatus',
            name='displayed_answers',
            field=models.ManyToManyField(blank=True, to='base.Answer'),
        ),
    ]