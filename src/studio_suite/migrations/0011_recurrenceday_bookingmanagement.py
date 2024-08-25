# Generated by Django 4.2 on 2023-10-06 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studio_suite', '0010_alter_kilnmanagement_kiln_max_temp'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecurrenceDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='BookingManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_recurring', models.IntegerField(choices=[(0, 'No'), (1, 'Yes')], default=0)),
                ('recurrence_frequency', models.CharField(blank=True, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], max_length=10, null=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('load_after_time', models.TimeField()),
                ('max_bookings', models.IntegerField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('kiln', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studio_suite.kilnmanagement')),
                ('recurrence_days', models.ManyToManyField(blank=True, null=True, to='studio_suite.recurrenceday')),
                ('studio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studio_suite.studioinfo')),
            ],
        ),
    ]