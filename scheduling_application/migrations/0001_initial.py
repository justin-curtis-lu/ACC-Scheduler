# Generated by Django 3.2.5 on 2021-09-19 06:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Senior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('address', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, default=None, max_length=30, null=True)),
                ('email', models.CharField(blank=True, default=None, max_length=40, null=True)),
                ('emergency_contacts', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('preferred_language', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('additional_notes', models.TextField(blank=True, default=None, null=True)),
                ('vaccinated', models.BooleanField(blank=True, default=None, null=True)),
                ('notify_email', models.BooleanField(default=None)),
                ('notify_text', models.BooleanField(default=None)),
                ('notify_call', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField(null=True)),
                ('year', models.IntegerField(null=True)),
                ('sent', models.BooleanField(default=False)),
                ('date_sent', models.CharField(default=None, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('galaxy_id', models.IntegerField(default=None, null=True)),
                ('last_name', models.CharField(max_length=30)),
                ('first_name', models.CharField(max_length=30)),
                ('phone', models.CharField(blank=True, default=None, max_length=30, null=True)),
                ('email', models.CharField(blank=True, default=None, max_length=40, null=True)),
                ('address', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('dob', models.CharField(blank=True, default=None, max_length=10, null=True)),
                ('minor', models.BooleanField(blank=True, default=False, editable=False, null=True)),
                ('vaccinated', models.BooleanField(blank=True, default=False, null=True)),
                ('notify_email', models.BooleanField(default=False)),
                ('notify_text', models.BooleanField(default=False)),
                ('notify_call', models.BooleanField(default=False)),
                ('additional_notes', models.TextField(blank=True, default=None, null=True)),
                ('survey_token', models.CharField(blank=True, default=None, max_length=32, null=True)),
                ('unsubscribed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(default=None, max_length=10, null=True)),
                ('_9_10', models.BooleanField(default=False)),
                ('_10_11', models.BooleanField(default=False)),
                ('_11_12', models.BooleanField(default=False)),
                ('_12_1', models.BooleanField(default=False)),
                ('_1_2', models.BooleanField(default=False)),
                ('all', models.BooleanField(default=False)),
                ('volunteer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Days', to='scheduling_application.volunteer')),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_address', models.CharField(blank=True, max_length=50, null=True)),
                ('end_address', models.CharField(blank=True, max_length=50, null=True)),
                ('date_and_time', models.CharField(max_length=50)),
                ('purpose_of_trip', models.TextField(blank=True, default=None, null=True)),
                ('notes', models.TextField(blank=True, default='N/A', null=True)),
                ('senior', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='scheduling_application.senior')),
                ('volunteer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Appointments', to='scheduling_application.volunteer')),
            ],
        ),
    ]
