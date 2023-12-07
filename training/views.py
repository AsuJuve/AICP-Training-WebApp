import requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.safestring import mark_safe
from .forms import SignupForm, LoginForm
from .helpers import get_chart_data, generate_recommendation
from .models import Competitor, Category, Level, Recommendation, Problem

@login_required
@require_POST
def request_recommendation(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    user_level = Level.objects.get(competitor=request.user, category=category)
    user_recommendations = Recommendation.objects.filter(competitor_id=request.user).values_list('problem_id', flat=True)
    problem_with_category = category.problems.all()

    # Only predict probability to solve problems that:
    # - Belong to the desired category
    # - Have not been recommended before
    problems = Problem.objects.filter(Q(pk__in=problem_with_category) & ~Q(pk__in=user_recommendations))
    
    recommended_problem = generate_recommendation(request.user, user_level, problems)

    recommendation = Recommendation.objects.create(
        competitor=request.user,
        problem=recommended_problem,
        level_before=user_level.level,
        created_at=timezone.now()
    )
    recommendation.save()

    messages.info(
        request,
        mark_safe(
            f"<a target='_blank' href='https://codeforces.com/problemset/problem/{recommended_problem.contest}/{recommended_problem.index}'>{recommended_problem.contest}{recommended_problem.index}</a>"
        )
    )
    return redirect('training:category_detail', category_id=category_id)

@login_required
def category_detail(request, category_id):
    # --- DATA ---
    category = get_object_or_404(Category, pk=category_id)
    problem_with_category = category.problems.all()
    user_level_exists = Level.objects.filter(competitor=request.user, category=category).exists()

    # Get all Recommendations that fulfill the following statements:
    # - Belong to problem that belongs to the category
    # - Created more than 2 hours ago OR the problem has been solved
    current_time = timezone.now()
    two_hours_ago = current_time - timezone.timedelta(hours=2)
    recommendations_chart = Recommendation.objects.filter(
        Q(problem_id__in=problem_with_category )
        & Q(Q(created_at__lte=two_hours_ago) | Q(verdict=True))
    )

    recommendations_table = Recommendation.objects.filter(
        Q(problem_id__in=problem_with_category )
    )

    if user_level_exists:
        user_level = Level.objects.get(competitor=request.user, category=category)
        chart = get_chart_data(recommendations_chart, category, user_level)
    else:
        chart = get_chart_data(recommendations_chart, category)

    # --- PAGINATION ---

    page = request.GET.get('page', 1)
    paginator = Paginator(recommendations_table, 10) 

    try:
        paginated_recommendations = paginator.page(page)
    except PageNotAnInteger:
        paginated_recommendations = paginator.page(1)
    except EmptyPage:
        paginated_recommendations = paginator.page(paginator.num_pages)

    return render(
        request,
        'categories/category_detail.html',
        {
            'category': category, 
            'chart': chart,
            'recommendations': paginated_recommendations
        })

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
