# Generated by Django 4.2.8 on 2023-12-06 19:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0004_alter_recomendation_level_after_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Recomendation',
            new_name='Recommendation',
        ),
    ]
