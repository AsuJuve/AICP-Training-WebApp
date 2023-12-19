from datetime import datetime
from django.conf import settings
from django.utils import timezone
from tensorflow.keras.models import load_model
from trueskill import Rating, rate_1vs1, setup
import math
import requests
import os
import pandas as pd
import plotly.graph_objects as go

# Set the TrueSkill backend to 'mpmath'
setup(backend='mpmath')

def get_chart_data(recommendations, category, user_level=None):
    fig = go.Figure()

    dates = [user_level.created_at] + [r.result_date for r in recommendations]
    dates = [date.astimezone(timezone.get_current_timezone()) for date in dates]
    levels = [800.0] + [r.level_after for r in recommendations]

    if user_level:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=levels,
                line=dict(color="#"+category.color, width=4)
            )
        )
    else:
        fig.add_annotation(
            text="Inicia el entrenamiento en la categoría para comenzar a ver tu progreso",
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=28
            )
        )

        fig.update_layout(
            xaxis=dict(
                visible=False
            ),
            yaxis=dict(
                visible=False
            )
        )

    chart = fig.to_html()

    return chart


def generate_recommendation(user_level, problems, desired_indexes):
    model_path = os.path.join(settings.BASE_DIR, 'training/prediction/recommendation_model.keras')
    recommendation_model = load_model(model_path)

    # DataFrame with the data for prediction
    data = {
        'user_rating': [normalize(user_level, 800.0, 3500.0)] * len(problems),
        'problem_difficulty': [problem.difficulty for problem in problems],
        'problem_solved_count': [problem.number_solutions for problem in problems],
        'problem_category_greedy': [1 if "greedy" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems],
        'problem_category_strings': [1 if "strings" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems],
        'problem_category_dynamic_programming': [1 if "dynamic programming" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems],
        'problem_category_math': [1 if "math" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems],
        'problem_category_sortings': [1 if "sortings" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems],
        'problem_category_trees': [1 if "trees" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems],
        'problem_category_data_structures': [1 if "data structures" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems],
        'problem_category_graphs': [1 if "graphs" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems],
        'problem_category_number_theory': [1 if "number theory" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems],
        'problem_category_bitmasks': [1 if "bitmasks" in problem.categories.all().values_list('name', flat=True) else 0 for problem in problems]
    }
    df = pd.DataFrame(data)
    predictions = recommendation_model.predict(df)
    
    # TODO - Add custom thresholds
    upper_threshold = .85
    lower_threshold = .65

    problem_predictions = list(zip(problems, predictions))
    problem_predictions = [(x, y) for x, y in problem_predictions if y >= lower_threshold and y <= upper_threshold]
    problem_predictions = sorted(problem_predictions, key = lambda p: p[1])

    recommended_problems = []
    for desired_index in desired_indexes:
        if desired_index[0] <= 1:
            index = desired_index[1]
        else:
            index = (len(problem_predictions) // desired_index[0]) + desired_index[1]
        recommended_problems.append(problem_predictions[index][0])
    
    return recommended_problems


def normalize(value, min_value, max_value):
    normalized = (value - min_value) / (max_value - min_value)

    # Keep values inside 0 and 1
    return max(0.0, min(normalized, 1.0))


def denormalize(normalized, min_value, max_value):
    denormalized = normalized * (max_value - min_value) + min_value

    return denormalized


def update_problem_recommendations(user_handle, recommendations):
    active_recommendations = []
    solved_recommendations = []
    not_solved_recommendations = []

    for recommendation in recommendations:

        # Check if the recommendation has been solved
        if recommendation.verdict == None:
            recommendation_solved = check_codeforces_submission(
                user_handle,
                recommendation.problem.contest,
                recommendation.problem.index,
                (5 if recommendation.is_for_diagnosis else 2)
            )

            if recommendation_solved:
                solved_recommendations.append(recommendation)
            else:
                if recommendation.is_for_diagnosis:
                    current_time = timezone.now()
                    five_hours_ago = current_time - timezone.timedelta(hours=5)

                    if recommendation.created_at > five_hours_ago:
                        active_recommendations.append(recommendation)
                    else:
                        not_solved_recommendations.append(recommendation)

                else:
                    current_time = timezone.now()
                    two_hours_ago = current_time - timezone.timedelta(hours=2)

                    if recommendation.created_at > two_hours_ago:
                        active_recommendations.append(recommendation)
                    else:
                        not_solved_recommendations.append(recommendation)

    return (active_recommendations, solved_recommendations, not_solved_recommendations)


def check_codeforces_submission(user_handle, contest_id, problem_index, max_hours_ago):
    response = requests.get(f'https://codeforces.com/api/user.status?handle={user_handle}')
    
    if response.status_code == 200:
        submissions = response.json().get('result', [])
        
        current_time = datetime.utcnow()

        for submission in submissions:
            # Check if the submission was sent more than max_hours_ago hours ago
            submission_time = datetime.utcfromtimestamp(submission.get('creationTimeSeconds'))
            time_difference = current_time - submission_time
            
            if time_difference.total_seconds() > max_hours_ago * 3600:
                break 
            
            if (
                submission.get('problem', {}).get('contestId') == contest_id and
                submission.get('problem', {}).get('index') == problem_index
            ):
                if submission.get('verdict') == 'OK':
                    return True  

    return False


def update_user_level(solved, user_level, problem_difficulty):
    user_level = Rating(mu=user_level.mu, sigma=user_level.sigma)
    problem_level = Rating(mu=denormalize(problem_difficulty, 800, 3500))

    # Update user's level based on the result
    if solved:
        new_user_level, _ = rate_1vs1(user_level, problem_level)
    else:
        _, new_user_level = rate_1vs1(user_level, problem_level)

    # Update the user's level in the database
    if math.ceil(new_user_level.mu) <= 800:
        new_user_level = Rating(mu=800, sigma=new_user_level.sigma)

    if math.floor(new_user_level.mu) >= 3500:
        new_user_level = Rating(mu=3500, sigma=new_user_level.sigma)

    return (new_user_level.mu, new_user_level.sigma)