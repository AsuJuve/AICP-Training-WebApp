from django.contrib.auth.models import AbstractUser
from django.db import models

class Competitor(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=False)

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
