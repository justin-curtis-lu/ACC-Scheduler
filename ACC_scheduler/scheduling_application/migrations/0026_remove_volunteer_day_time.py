# Generated by Django 3.2.5 on 2021-08-09 23:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_application', '0025_auto_20210809_1634'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='volunteer',
            name='day_time',
        ),
    ]
