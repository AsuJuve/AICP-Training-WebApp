from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models

class Competitor(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    email = models.EmailField(unique=True, blank=False, null=False, verbose_name="Correo electrónico")
    username = models.CharField(
        validators=[
            MinLengthValidator(3, message="El nombre de usuario debe tener mínimo 3 caracteres"),
            MaxLengthValidator(24, message="El nombre de usuario debe tener máximo 24 caracteres")
        ],
        max_length=24,
        unique=False,
        verbose_name="Usuario de Codeforces"
    )
    password = models.TextField(
        max_length=32,
        validators=[
            MinLengthValidator(8, message="La contraseña tener mínimo 8 caracteres"),
            MaxLengthValidator(32, message="La contraseña tener máximo 32 caracteres")
        ],
        verbose_name="Contraseña"
    )

    def __str__(self):
        return self.email

class Category(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=6)

class Problem(models.Model):
    contest = models.IntegerField()
    index = models.CharField(max_length=1)
    difficulty = models.FloatField()
    number_solutions = models.IntegerField()

class Recomendation(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    verdict = models.BooleanField()
    started = models.DateTimeField()
    level_before = models.FloatField()
    level_after = models.FloatField()

class Level(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    level = models.FloatField()
    started = models.DateTimeField()

class ProblemCategory(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)