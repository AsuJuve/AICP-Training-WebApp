# Generated by Django 4.2.8 on 2023-12-07 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0009_problem_categories_delete_problemcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='problems', to='training.category'),
        ),
    ]
