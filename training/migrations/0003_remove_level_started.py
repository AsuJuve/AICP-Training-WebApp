# Generated by Django 4.2.8 on 2023-12-06 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0002_alter_competitor_email_alter_competitor_password_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='level',
            name='started',
        ),
    ]