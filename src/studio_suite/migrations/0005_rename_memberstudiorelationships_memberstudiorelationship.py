# Generated by Django 4.2 on 2023-09-27 01:27

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('studio_suite', '0004_memberstudiorelationships'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MemberStudioRelationships',
            new_name='MemberStudioRelationship',
        ),
    ]