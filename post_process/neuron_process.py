import numpy as np
import pandas as pd
import dash
from dash import dcc, html, ctx
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import webbrowser
from threading import Timer




# Load and process your data as before
n_morph = 73
file_path = f"./neurons_morph/neuron_skel_{n_morph}.swc" 
data = np.loadtxt(file_path)

soma = data[data[:, 1] == 1][0]
id_soma = int(soma[0])
first_children = np.array(data[data[:, 6] == id_soma, 0],dtype=int)

leafes = np.array(data[data[:, 1] == 6,0],dtype=int)
branches = [[] for i in range(len(leafes))]
branches_stack = [[] for i in range(len(first_children))]

for i,id in enumerate(leafes):
    parent_id = 0
    while parent_id != id_soma:
        point = data[data[:, 0] == id][0]
        parent_id = int(point[6])
        branches[i].append(id)
        if parent_id == id_soma:
            id_branch = np.where(first_children == id)[0][0]
            branches_stack[id_branch].append(branches[i])
            continue
        parent_point = data[data[:, 0] == parent_id]
        id = parent_id

for i,branch in enumerate(branches_stack):
    branches_stack[i] = np.unique(np.concatenate(branch))

edge_x, edge_y, edge_z = [], [], []

points = np.zeros((len(data),4))
for i,point in enumerate(data):
    parent_id = int(point[6])

    if parent_id != -1:
        parent_point = data[data[:, 0] == parent_id][0]
        edge_x += [point[2], parent_point[2], None]
        edge_y += [point[3], parent_point[3], None]
        edge_z += [point[4], parent_point[4], None]
    
    points[i,0] = point[0]
    points[i,1] = point[2]
    points[i,2] = point[3]
    points[i,3] = point[4] 

button_clicked = []
id_branch = 0

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = [
    html.Div(children = f'Visualizing morphology n. {n_morph}'),
    html.Div( id = 'Branch_output'),
    html.Div( id = 'Button_sel'),
    html.Div([
    dcc.Graph(id='3d-plot'),
    html.Button('Next Branch', id='next_branch-button', n_clicks=0),
    html.Button('Axon', id='Axon', n_clicks=0),
    html.Button('Basal Dendrite', id='B_Dendrite', n_clicks=0),
    html.Button('Apical Dendrite', id='A_Dendrite', n_clicks=0),
    html.Button('RESET MORPHOLOGY', id='reset', n_clicks=0),
    dcc.Store(id='click-store', data={'next_branch': 0})
])
]
# Define the callback function to update the plot
@app.callback(
    Output('3d-plot', 'figure'),
    Output('Branch_output', 'children'),
    Output('Button_sel', 'children'),
    Output('click-store', 'data'),
    Input('next_branch-button', 'n_clicks'),
    Input('Axon', 'n_clicks'),
    Input('B_Dendrite', 'n_clicks'),
    Input('A_Dendrite', 'n_clicks'),
    Input('reset', 'n_clicks'),
    State('click-store', 'data')
)
def update_plot(next_branch, axon, a_dendrite, b_dendrite, reset, click_data):
    print(click_data['next_branch'])
    global button_clicked
    global id_branch
    fig = go.Figure()

    # Add the edge trace
    edge_trace = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='black', width=2))
    fig.add_trace(edge_trace)

    # Add the point trace
    point_trace = go.Scatter3d(x=points[:,1], y=points[:,2], z=points[:,3], mode='markers',
                            marker=dict(size=2, color='blue'),
                            text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in data],
                            hoverinfo='text')
    fig.add_trace(point_trace)
    soma_trace = go.Scatter3d(x=[soma[2]], y=[soma[3]], z=[soma[4]], mode='markers',
                            marker=dict(size=5, color='grey'),
                            text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in data],
                            hoverinfo='text')
    fig.add_trace(soma_trace)

    if button_clicked != None:
        for i,color in enumerate(button_clicked):
            branch = branches_stack[i]
            point_x = points[np.isin(points[:,0],branch),1]
            point_y = points[np.isin(points[:,0],branch),2]
            point_z = points[np.isin(points[:,0],branch),3]

            fig.add_trace(go.Scatter3d(x=point_x, y=point_y, z=point_z, mode='markers',
                                marker=dict(size=2, color=color),
                                text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in data],
                                hoverinfo='text'))
            
    if (button_clicked != None and "reset" == ctx.triggered_id):
        click_data['next_branch'] = 0
        button_clicked = []
        branch_info = None
        branch_type_selected = None
        fig = go.Figure()

        # Add the edge trace
        edge_trace = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='black', width=2))
        fig.add_trace(edge_trace)

        # Add the point trace
        point_trace = go.Scatter3d(x=points[:,1], y=points[:,2], z=points[:,3], mode='markers',
                                marker=dict(size=2, color='blue'),
                                text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in data],
                                hoverinfo='text')
        fig.add_trace(point_trace)
        soma_trace = go.Scatter3d(x=[soma[2]], y=[soma[3]], z=[soma[4]], mode='markers',
                                marker=dict(size=5, color='grey'),
                                text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in data],
                                hoverinfo='text')
        fig.add_trace(soma_trace)
        return fig, branch_info, branch_type_selected, click_data

    # Loop through the branches and add them to the figure
    if  "next_branch-button" == ctx.triggered_id:
        click_data['next_branch'] += 1  
        id_branch = click_data['next_branch']
        if id_branch > len(branches_stack):
            branch_info = None
            branch_type_selected = None
            return fig, branch_info, branch_type_selected, click_data
        else:
            branch = branches_stack[id_branch-1]
            point_x = points[np.isin(points[:,0],branch),1]
            point_y = points[np.isin(points[:,0],branch),2]
            point_z = points[np.isin(points[:,0],branch),3]

            fig.add_trace(go.Scatter3d(x=point_x, y=point_y, z=point_z, mode='markers',
                                    marker=dict(size=2, color='red'),
                                    text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in data],
                                    hoverinfo='text'))

    if "Axon" == ctx.triggered_id:
        color = 'violet'
        branch_type = 2
        button_clicked.append(color)

    elif "B_Dendrite" == ctx.triggered_id:
        color = 'yellow'
        branch_type = 3
        button_clicked.append(color)
 
    elif "A_Dendrite" == ctx.triggered_id:
        color = 'green'
        branch_type = 4
        button_clicked.append(color)

    if ctx.triggered_id == (axon or b_dendrite or a_dendrite):
    # Add the branch trace to the existing figure
        fig.add_trace(go.Scatter3d(x=point_x, y=point_y, z=point_z, mode='markers',
                                marker=dict(size=2, color=color),
                                text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in data],
                                hoverinfo='text'))

    # Update the layout
    fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    branch_info = f"Selected Branch: {id_branch}"
    if "next_branch-button" == ctx.triggered_id:
        branch_type_selected = f"Branch {id_branch} selected as :"
    else:
        branch_type_selected = f"Branch {id_branch} selected as {ctx.triggered_id}"

    return fig, branch_info, branch_type_selected, click_data

def open_browser():
      webbrowser.open_new("http://127.0.0.1:8050")

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run_server(debug=True)