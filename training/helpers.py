from django.conf import settings
from tensorflow.keras.models import load_model
import os
import pandas as pd
import plotly.graph_objects as go

def get_chart_data(recommendations, category, user_level=None):
    fig = go.Figure()

    if len(recommendations) > 0 or user_level:
        fig.add_trace(
            go.Scatter(
                x=[user_level.created_at] + [r.created_at for r in recommendations],
                y=[0.0] + [r.level_after for r in recommendations],
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


def generate_recommendation(user, user_level, problems):
    model_path = os.path.join(settings.BASE_DIR, 'training/prediction/recommendation_model.keras')
    recommendation_model = load_model(model_path)

    # Create a DataFrame with the data for prediction
    data = {
        'user_rating': [user_level.level] * len(problems),
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
    recommended_problem = problem_predictions[-1][0]
    
    return recommended_problem
