# Generated by Django 2.2.2 on 2019-06-25 14:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20190625_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamestatus',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]