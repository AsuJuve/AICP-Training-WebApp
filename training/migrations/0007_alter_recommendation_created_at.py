# Generated by Django 4.2.8 on 2023-12-06 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0006_alter_recommendation_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recommendation',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]