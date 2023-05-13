# Generated by Django 4.1.3 on 2023-03-27 21:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_passager_reservation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passager',
            name='age',
        ),
        migrations.AddField(
            model_name='passager',
            name='email',
            field=models.EmailField(default=datetime.datetime(2023, 3, 27, 21, 0, 54, 462445, tzinfo=datetime.timezone.utc), max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='passager',
            name='numero',
            field=models.CharField(default=1, max_length=11),
            preserve_default=False,
        ),
    ]