# Generated by Django 4.2 on 2023-10-05 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studio_suite', '0009_alter_kilnmanagement_kiln_max_temp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kilnmanagement',
            name='kiln_max_temp',
            field=models.CharField(choices=[('Cone 022', 'Cone 022'), ('Cone 018', 'Cone 018'), ('Cone 06', 'Cone 06'), ('Cone 04', 'Cone 04'), ('Cone 03', 'Cone 03'), ('Cone 5', 'Cone 5'), ('Cone 4', 'Cone 4'), ('Cone 02', 'Cone 02'), ('Cone 1', 'Cone 1'), ('Cone 10', 'Cone 10')], max_length=100),
        ),
    ]
