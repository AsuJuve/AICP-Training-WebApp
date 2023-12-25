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
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=6)

    def __str__(self):
        return self.name

class Problem(models.Model):
    contest = models.IntegerField()
    index = models.CharField(max_length=3)
    difficulty = models.FloatField()
    number_solutions = models.IntegerField()
    categories = models.ManyToManyField(Category, related_name='problems', blank=True)

    def __str__(self):
        return str(self.contest) + str(self.index)

class Recommendation(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    verdict = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    result_date = models.DateTimeField(blank=True, null=True)
    is_for_diagnosis = models.BooleanField()
    level_before = models.FloatField(blank=True, null=True)
    level_after = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ('result_date',)

    def __str__(self):
        return str(self.competitor) + " - " +str(self.problem)

class Level(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    mu = models.FloatField()
    sigma = models.FloatField()
    created_at = models.DateTimeField()

    def __str__(self):
        return str(self.competitor) + " - " + str(self.category)
