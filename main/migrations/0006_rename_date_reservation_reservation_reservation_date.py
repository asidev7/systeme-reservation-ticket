# Generated by Django 4.1.3 on 2023-03-27 22:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_rename_passager_passenger_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservation',
            old_name='date_reservation',
            new_name='reservation_date',
        ),
    ]
