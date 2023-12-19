from django.conf import settings
from django.utils import timezone
from tensorflow.keras.models import load_model
import os
import pandas as pd
import plotly.graph_objects as go


def get_chart_data(recommendations, category, user_level=None):
    fig = go.Figure()

    dates = [user_level.created_at] + [r.result_date for r in recommendations]
    dates = [date.astimezone(timezone.get_current_timezone()) for date in dates]
    
    levels = [800.0] + [r.level_after for r in recommendations]

    print(dates)
    print(levels)

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

    # Create a DataFrame with the data for prediction
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

    # Use your trained model to make predictions (replace this with your actual model)
    
    predictions = recommendation_model.predict(df)

    upper_threshold = .85
    lower_threshold = .65

    problem_predictions = list(zip(problems, predictions))
    problem_predictions = [(x, y) for x, y in problem_predictions if y >= lower_threshold and y <= upper_threshold]
    problem_predictions = sorted(problem_predictions, key = lambda p: p[1])

    print(len(problem_predictions))
    recommended_problems = []
    for desired_index in desired_indexes:
        if desired_index[0] <= 1:
            index = desired_index[1]
        else:
            index = (len(problem_predictions) // desired_index[0]) + desired_index[1]
        print(index)
        recommended_problems.append(problem_predictions[index][0])
    
    return recommended_problems


def normalize(value, min_value, max_value):
    normalized = (value - min_value) / (max_value - min_value)

    # Keep values inside 0 and 1
    return max(0.0, min(normalized, 1.0))


def get_active_problem_recommendations(recommendations):
    active_recommendations = []

    for recommendation in recommendations:
        if recommendation.is_for_diagnosis:
            current_time = timezone.now()
            five_hours_ago = current_time - timezone.timedelta(hours=5)

            if recommendation.created_at > five_hours_ago:
                active_recommendations.append(recommendation)

        else:
            current_time = timezone.now()
            two_hours_ago = current_time - timezone.timedelta(hours=2)

            if recommendation.created_at > two_hours_ago:
                active_recommendations.append(recommendation)

    return active_recommendations
