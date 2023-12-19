import requests
from datetime import datetime, timedelta
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
from .helpers import get_chart_data, generate_recommendation, update_problem_recommendations, update_user_level
from .models import Competitor, Category, Level, Recommendation, Problem

@login_required
@require_POST
def request_recommendation(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    user_level = Level.objects.get(competitor=request.user, category=category)
    user_recommendations = Recommendation.objects.filter(competitor_id=request.user).values_list('problem_id', flat=True)
    problems_with_category = category.problems.all()

    # Only predict probability to solve problems that:
    # - Belong to the desired category
    # - Have not been recommended before
    problems = Problem.objects.filter(Q(pk__in=problems_with_category) & ~Q(pk__in=user_recommendations))
    
    desired_index = (0, 0)
    recommended_problems = generate_recommendation(user_level.mu, problems, [desired_index])

    recommendation = Recommendation.objects.create(
        competitor=request.user,
        problem=recommended_problems[0],
        level_before=user_level.mu,
        is_for_diagnosis=False,
        created_at=timezone.now()
    )
    recommendation.save()

    # Initiate level for categories
    problem_categories = recommended_problems[0].categories.all()

    for c in problem_categories:
        user_level_exists = Level.objects.filter(competitor=request.user, category=c).exists()

        if not user_level_exists:
            level = Level.objects.create(
                competitor=request.user,
                category=c,
                mu=800.0,
                sigma=8.333333333333334,
                created_at=timezone.now()
            )

            level.save()

    return redirect('training:category_detail', category_id=category_id)

@login_required
@require_POST
def request_diagnosis(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    user_recommendations = Recommendation.objects.filter(competitor_id=request.user).values_list('problem_id', flat=True)
    problems_with_category = category.problems.all()

    # Only predict probability to solve problems that:
    # - Belong to the desired category
    # - Have not been solved by the user before
    problems = Problem.objects.filter(Q(pk__in=problems_with_category) & ~Q(pk__in=user_recommendations))
    
    # Generate problem recommendations for diagnosis

    # Get problems with different indexes
    desired_indexes = [
        (0, 0),
        (0, 1),
        (5, 0),
        (5, 1),
        (3, 0),
        (2, 0)
    ]

    recommended_problems = generate_recommendation(800.0, problems, desired_indexes)

    for recommended_problem in recommended_problems:
        recommendation = Recommendation.objects.create(
            competitor=request.user,
            problem=recommended_problem,
            level_before=800.0,
            is_for_diagnosis=True,
            created_at=timezone.now()
        )
        recommendation.save()

        # Initiate level for categories
        problem_categories = recommended_problem.categories.all()

        for c in problem_categories:
            user_level_exists = Level.objects.filter(competitor=request.user, category=c).exists()

            if not user_level_exists:
                level = Level.objects.create(
                    competitor=request.user,
                    category=c,
                    mu=800.0,
                    sigma=8.333333333333334,
                    created_at=timezone.now()
                )
                
                level.save()

    return redirect('training:category_detail', category_id=category_id)

@login_required
def category_detail(request, category_id):

    # --- UPDATE RECOMMENDATIONS AND PROGRESS CHART---
    category = get_object_or_404(Category, pk=category_id)
    problem_with_category = category.problems.all()
    user_level_exists = Level.objects.filter(competitor=request.user, category=category).exists()

    # Get all Recommendations that belong to problem that belongs to the category
    category_recommendations = Recommendation.objects.filter(problem_id__in=problem_with_category)
    updated_category_recommendations = update_problem_recommendations(request.user, category_recommendations)
    active_recommendations = update_problem_recommendations(request.user, Recommendation.objects.all())[0]

    user_level = None
    if user_level_exists:
        user_level = Level.objects.get(competitor=request.user, category=category)
        # --- UPDATE USER LEVEL ---

        solved_recommendations = updated_category_recommendations[1]
        not_solved_recommendations = updated_category_recommendations[2]

        for solved_recommendation in solved_recommendations:
            new_user_level = update_user_level(
                True,
                user_level,
                solved_recommendation.problem.difficulty
            )

            user_level.mu = new_user_level[0]
            user_level.sigma = new_user_level[1]
            user_level.save()

            solved_recommendation.verdict = True
            solved_recommendation.result_date = timezone.now()
            solved_recommendation.level_after = user_level.mu
            solved_recommendation.save()

        for not_solved_recommendation in not_solved_recommendations:
            new_user_level = update_user_level(
                False,
                user_level,
                not_solved_recommendation.problem.difficulty
            )

            user_level.mu = new_user_level[0]
            user_level.sigma = new_user_level[1]
            user_level.save()

            not_solved_recommendation.verdict = False
            not_solved_recommendation.result_date = timezone.now()
            not_solved_recommendation.level_after = user_level.mu
            not_solved_recommendation.save()

        recommendations_chart = Recommendation.objects.filter(
            (~Q(pk__in=[ar.pk for ar in updated_category_recommendations[0]]) & Q(pk__in=[ar.pk for ar in category_recommendations]))
            | 
            (Q(verdict=True) & Q(pk__in=[ar.pk for ar in category_recommendations]))
        )
            
        chart = get_chart_data(recommendations_chart, category, user_level)
    else:

        recommendations_chart = Recommendation.objects.filter(
            (~Q(pk__in=[ar.pk for ar in updated_category_recommendations[0]]) & Q(pk__in=[ar.pk for ar in category_recommendations]))
            | 
            (Q(verdict=True) & Q(pk__in=[ar.pk for ar in category_recommendations]))
        )

        chart = get_chart_data(recommendations_chart, category)

    # --- PAGINATION ---
    page = request.GET.get('page', 1)
    paginator = Paginator(category_recommendations, 10) 

    try:
        paginated_recommendations = paginator.page(page)
    except PageNotAnInteger:
        paginated_recommendations = paginator.page(1)
    except EmptyPage:
        paginated_recommendations = paginator.page(paginator.num_pages)

    # --- RENDER ---

    return render(
        request,
        'categories/category_detail.html',
        {
            'category': category, 
            'chart': chart,
            'active_recommendations_category': updated_category_recommendations[0],
            'active_recommendations': active_recommendations,
            'recommendations': paginated_recommendations,
            'user_level': user_level
        })

@login_required
def home(request):
    categories = Category.objects.all()
    levels = Level.objects.filter(competitor=request.user)
    user_levels = {level.category_id: level.mu for level in levels}

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
