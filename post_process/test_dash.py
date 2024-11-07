import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np

# Sample data
np.random.seed(0)
points = np.random.rand(100, 3)  # 100 random 3D points
colors = ['blue'] * 100  # Initial color for all points

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    dcc.Graph(id='3d-scatter-plot'),
    html.Button('Next Branch', id='select-button', n_clicks=0),
])

# Callback to update the 3D scatter plot
@app.callback(
    Output('3d-scatter-plot', 'figure'),
    Input('select-button', 'n_clicks')
)
def update_graph(n_clicks):
    # Create a scatter plot
    fig = go.Figure()

    # Add a scatter trace for points
    fig.add_trace(go.Scatter3d(
        x=points[:, 0],
        y=points[:, 1],
        z=points[:, 2],
        mode='markers',
        marker=dict(size=5, color=colors),  # Use colors list
        text=[f'Point {i}' for i in range(len(points))],
        hoverinfo='text'
    ))

    # Update layout
    fig.update_layout(scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    ))

    # Randomly select a few points to change their color on button click
    if n_clicks > 0:
        selected_indices = np.random.choice(len(points), size=5, replace=False)
        for index in selected_indices:
            colors[index] = 'red'  # Change selected points to red

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
