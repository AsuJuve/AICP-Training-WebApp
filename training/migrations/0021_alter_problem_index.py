# Generated by Django 4.2.8 on 2023-12-25 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0020_remove_recommendation_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='index',
            field=models.CharField(max_length=3),
        ),
    ]