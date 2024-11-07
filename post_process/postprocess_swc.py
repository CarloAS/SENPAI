import numpy as np
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

# Load SWC Data
def load_swc(file_path):
    data = np.loadtxt(file_path)
    return data

def find_soma(data):
    soma = data[data[:, 1] == 1][0]
    return soma[2:5]

def get_children(data, parent_id):
    return data[data[:, 6] == parent_id]

def plot_neuron(data, selected_branch=None):
    edge_x, edge_y, edge_z = [], [], []
    point_x, point_y, point_z = [], [], []

    for point in data:
        parent_id = int(point[6])
        if parent_id != -1:
            parent_point = data[data[:, 0] == parent_id][0]
            edge_x += [point[2], parent_point[2], None]
            edge_y += [point[3], parent_point[3], None]
            edge_z += [point[4], parent_point[4], None]
        
        point_x.append(point[2])
        point_y.append(point[3])
        point_z.append(point[4])

    edge_trace = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z,
                                mode='lines',
                                line=dict(color='black', width=2))

    point_trace = go.Scatter3d(x=point_x, y=point_y, z=point_z,
                                 mode='markers',
                                 marker=dict(size=3, color='blue',opacity = 0.5),
                                 text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in data],
                                 hoverinfo='text')

    fig = go.Figure(data=[edge_trace, point_trace])
    """soma = find_soma(data)
    fig.update_layout(scene_camera=dict(
        eye=dict(x=0, y=-1.5, z=0.5),
        center=dict(x=soma[0], y=soma[1], z=soma[2])
    ))"""
    fig.update_layout(scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    ))
    return fig

def label_branch(data, branch_id, label_type):
    data[data[:, 0] == branch_id, 1] = label_type
    children = get_children(data, branch_id)
    for child in children:
        label_branch(data, int(child[0]), label_type)
    return data

# Initialize the Dash app
app = dash.Dash(__name__)

# Load the SWC data
file_path = "../neurons_morph/neuron_skel_6.swc"  # Replace with your file path
data = load_swc(file_path)

# App layout
app.layout = html.Div([
    dcc.Graph(figure=plot_neuron(data),id='neuron-plot', config={'displayModeBar': True}),
    html.Div(id='branch-info', style={'margin-top': '20px'}),
    dcc.Dropdown(
        id='branch-selector',
        options=[
            {'label': 'Axon', 'value': 2},
            {'label': 'Basal Dendrite', 'value': 3},
            {'label': 'Apical Dendrite', 'value': 4}
        ],
        value=2,  # Default selection
        clearable=False,
        style={'width': '50%'}
    ),
    html.Button('Apply', id='apply-button', n_clicks=0),
    html.Div(id='output-container', style={'margin-top': '20px'})
])

# Callback to update the plot and branch info on point selection
@app.callback(
    Output('neuron-plot', 'figure'),
    Output('branch-info', 'children'),
    Output('output-container', 'children'),
    Input('neuron-plot', 'clickData'),
    Input('apply-button', 'n_clicks'),
    Input('branch-selector', 'value'),
)
def update_graph(clickData, n_clicks, selected_type):
    global data  # Access the global data variable
    selected_branch_info = None

    if clickData is not None:
        point_id = int(clickData['points'][0]['text'].split(': ')[1].split(',')[0])
        selected_branch_info = f"Selected branch ID: {point_id}"
        
        # Label the branch with the selected type
        data = label_branch(data, point_id, selected_type)

    fig = plot_neuron(data, selected_branch=selected_branch_info)
    return fig, selected_branch_info, ""

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)