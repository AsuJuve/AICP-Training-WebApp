# Generated by Django 4.2.8 on 2023-12-06 08:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitor',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Correo electrónico'),
        ),
        migrations.AlterField(
            model_name='competitor',
            name='password',
            field=models.TextField(max_length=32, validators=[django.core.validators.MinLengthValidator(8, message='La contraseña tener mínimo 8 caracteres'), django.core.validators.MaxLengthValidator(32, message='La contraseña tener máximo 32 caracteres')], verbose_name='Contraseña'),
        ),
        migrations.AlterField(
            model_name='competitor',
            name='username',
            field=models.CharField(max_length=24, validators=[django.core.validators.MinLengthValidator(3, message='El nombre de usuario debe tener mínimo 3 caracteres'), django.core.validators.MaxLengthValidator(24, message='El nombre de usuario debe tener máximo 24 caracteres')], verbose_name='Usuario de Codeforces'),
        ),
    ]