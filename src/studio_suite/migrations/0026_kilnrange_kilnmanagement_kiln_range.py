# Generated by Django 4.2 on 2023-11-26 01:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studio_suite', '0025_alter_timeslotmanagement_min_role_required'),
    ]

    operations = [
        migrations.CreateModel(
            name='KilnRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('range_name', models.CharField(max_length=100)),
                ('min_temp', models.CharField(choices=[('Cone 022', 'Cone 022'), ('Cone 018', 'Cone 018'), ('Cone 06', 'Cone 06'), ('Cone 04', 'Cone 04'), ('Cone 03', 'Cone 03'), ('Cone 5', 'Cone 5'), ('Cone 4', 'Cone 4'), ('Cone 02', 'Cone 02'), ('Cone 1', 'Cone 1'), ('Cone 10', 'Cone 10')], max_length=100)),
                ('max_temp', models.CharField(choices=[('Cone 022', 'Cone 022'), ('Cone 018', 'Cone 018'), ('Cone 06', 'Cone 06'), ('Cone 04', 'Cone 04'), ('Cone 03', 'Cone 03'), ('Cone 5', 'Cone 5'), ('Cone 4', 'Cone 4'), ('Cone 02', 'Cone 02'), ('Cone 1', 'Cone 1'), ('Cone 10', 'Cone 10')], max_length=100)),
                ('studio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studio_suite.studioinfo')),
            ],
        ),
        migrations.AddField(
            model_name='kilnmanagement',
            name='kiln_range',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='studio_suite.kilnrange'),
        ),
    ]
