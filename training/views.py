from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import SignupForm, LoginForm
from .helpers import get_chart_data
from .models import Competitor, Category, Level, Recommendation, ProblemCategory
import requests

@login_required
def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    # Get all ProblemCategory objects for the specified category, retrieve only the problem id
    problem_category_ids = ProblemCategory.objects.filter(category_id=category_id).values_list('problem_id', flat=True)

    # Get all Recommendations that fulfill the following statements:
    # - Belong to problem that belong to the category
    # - Created more than 2 hours ago OR the problem has been solved
    current_time = timezone.now()
    two_hours_ago = current_time - timezone.timedelta(minutes=2)
    recommendations = Recommendation.objects.filter(
        Q(problem_id__in=problem_category_ids )
        & Q(Q(created_at__lte=two_hours_ago) | Q(verdict=True))
    )

    chart = get_chart_data(recommendations, category)
    
    return render(request, 'categories/category_detail.html', {'category': category, 'chart': chart})

@login_required
def home(request):
    categories = Category.objects.all()
    levels = Level.objects.filter(competitor=request.user)
    user_levels = {level.category_id: level.level for level in levels}

    return render(request, "home.html", {'categories': categories, 'user_levels': user_levels})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if the user exists in Codeforces
            api_url = f'https://codeforces.com/api/user.info?handles={username}'
            response = requests.get(api_url)
            data = response.json()

            if response.status_code != 200:
                if data.get('status') != 'OK':
                    return render(request, 'accounts/signup.html', {
                        'form': form,
                        'error_message': 'Usuario de Codeforces incorrecto'
                    })
                
                return render(request, 'accounts/signup.html', {
                    'form': form,
                    'error_message': 'Conexión fallida con la API de Codeforces. Intente de nuevo más tarde.'
                })

            user = Competitor.objects.create_user(email=email, username=username, password=password)
            login(request, user)

            return redirect('training:home')

    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})

class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
