from django.contrib import admin
from .models import Competitor, Category, Problem, ProblemCategory, Level

admin.site.register(Category)
admin.site.register(Competitor)
admin.site.register(Level)
admin.site.register(Problem)
admin.site.register(ProblemCategory)