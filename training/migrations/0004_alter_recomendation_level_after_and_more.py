# Generated by Django 4.2.8 on 2023-12-06 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_remove_level_started'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recomendation',
            name='level_after',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recomendation',
            name='level_before',
            field=models.FloatField(blank=True, null=True),
        ),
    ]