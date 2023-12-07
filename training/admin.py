from django.contrib import admin
from .models import Competitor, Category, Problem, Level, Recommendation

admin.site.register(Category)
admin.site.register(Competitor)
admin.site.register(Level)
admin.site.register(Problem)
admin.site.register(Recommendation)
