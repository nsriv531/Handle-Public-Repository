# Generated by Django 4.2 on 2023-11-06 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studio_suite', '0023_alter_memberstudiorelationship_member_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslotmanagement',
            name='min_role_required',
            field=models.CharField(choices=[('NA', 'No Access Member'), ('RM', 'Regular Member'), ('TECH', 'Technician'), ('MANAGER', 'Studio Manager')], default='NA', max_length=7),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='memberstudiorelationship',
            name='member_role',
            field=models.CharField(choices=[('NA', 'No Access Member'), ('RM', 'Regular Member'), ('TECH', 'Technician'), ('MANAGER', 'Studio Manager')], max_length=7),
        ),
        migrations.AlterField(
            model_name='studioinfo',
            name='new_member_role',
            field=models.CharField(choices=[('NA', 'No Acccess Member'), ('RM', 'Regular Member')], max_length=2),
        ),
    ]
