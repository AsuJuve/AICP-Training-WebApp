import plotly.graph_objects as go

def get_chart_data(recommendations, category):
    fig = go.Figure()

    if len(recommendations) <= 0:
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
    else:
        fig.add_trace(
            go.Scatter(
                x=[r.created_at for r in recommendations],
                y=[r.level_after for r in recommendations],
                line=dict(color="#"+category.color, width=4)
            )
        )

    chart = fig.to_html()

    return chart
