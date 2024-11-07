import numpy as np
import pandas as pd
import os
import dash
from dash import dcc, html, ctx
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import webbrowser
from threading import Timer
import regex as re
from NeuronMorphology import NeuronMorphology
import sys


class NeuronEditor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.swc_files = self.load_files(folder_path)
        self.current_file_index = 0
        self.selected_branch = None
        self.button_clicked = []
        self.id_branch = 0
        self.initialize_current_file()

    def load_files(self,folder_path):
        # Initialize an empty list to store file paths
        file_paths = []

        # Iterate through each file in the given folder
        for filename in os.listdir(folder_path):
            # Construct the full path
            full_path = os.path.join(folder_path, filename)
            
            # Check if it is a file (not a directory)
            if os.path.isfile(full_path):
                file_paths.append(full_path)

        return sorted(file_paths)
    
    def initialize_current_file(self):
        if self.swc_files:
            self.initialize_morphology(self.swc_files[self.current_file_index])
            
    def next_file(self):
        if self.current_file_index < len(self.swc_files) - 1:
            self.current_file_index += 1
            self.button_clicked = []
            self.id_branch = 0
            self.initialize_current_file()
            return True
        return False
    def load_data(self, file):
        # Load morphology from .swc file
        data = np.loadtxt(file)
        
        return data

    def initialize_morphology(self, file):
        
        morphology = NeuronMorphology(file)

        self.n_morph = morphology.n_morph
        self.data = morphology.data
        self.soma = morphology.soma
        self.leafes = morphology.leafes
        self.first_children = morphology.first_children
        self.branches_stack = morphology.branches_stack
        self.points = morphology.points
        self.edges = morphology.edges

        return
    
    def plot_morphology(self):

        edge_x = self.edges[0]
        edge_y = self.edges[1]
        edge_z = self.edges[2]
        points = self.points
        soma = self.soma

        fig = go.Figure()

        # Add the edge trace
        edge_trace = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='black', width=2))
        fig.add_trace(edge_trace)

        # Add the point trace
        point_trace = go.Scatter3d(x=points[:,1], y=points[:,2], z=points[:,3], mode='markers',
                                marker=dict(size=2, color='blue'),
                                text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in self.data],
                                hoverinfo='text')
        fig.add_trace(point_trace)
        soma_trace = go.Scatter3d(x=[soma[2]], y=[soma[3]], z=[soma[4]], mode='markers',
                                marker=dict(size=5, color='grey'),
                                text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in self.data],
                                hoverinfo='text')
        fig.add_trace(soma_trace)

        return fig
    
    def color_processed_branches(self):
        button_clicked = self.button_clicked
        points = self.points
        branches_stack = self.branches_stack

        for i,color in enumerate(button_clicked):
            branch = branches_stack[i]
            point_update = self.take_branch_points(branch)
            self.add_trace_branch(point_update,color)

        return

    def take_branch_points(self, branch):
        points = self.points
        point_x = points[np.isin(points[:,0],branch),1]
        point_y = points[np.isin(points[:,0],branch),2]
        point_z = points[np.isin(points[:,0],branch),3]
        point_update = [point_x,point_y,point_z]

        return point_update
    
    def add_trace_branch(self,point_update,color):
        self.fig.add_trace(go.Scatter3d(x=point_update[0], y=point_update[1], z=point_update[2], mode='markers',
                            marker=dict(size=2, color=color),
                            text=[f'ID: {int(pt[0])}, Type: {int(pt[1])}' for pt in self.data],
                            hoverinfo='text'))
        return 

    def reset(self, click_data):
        click_data['next_branch_click'] = 0
        self.button_clicked = []
        self.branch_info = None
        self.branch_type_selected = None
        fig = self.plot_morphology()
        return fig
    
    def next_branch(self, next_branch):
        branches_stack = self.branches_stack
        if next_branch > len(branches_stack):
            self.branch_info = None
            self.branch_type_selected = None
        else:
            branch = branches_stack[next_branch-1]
            point_update = self.take_branch_points(branch)
            self.add_trace_branch(point_update,'red')
        
        return point_update
    
    def update_branch_type(self, branch_type, id_branch):
        data = self.data
        branch = self.branches_stack[id_branch-1]
        ind_nodes = np.where(data[:,0] == branch)
        data[ind_nodes,1] = branch_type
        self.data = data
        
        return

    def initialize_app(self):
        # Create the Dash app
        app = dash.Dash(__name__)
        # Define the layout
        app.layout = html.Div([
            html.H1(children=f'Visualizing morphology n. {self.n_morph}', id='title'),
            html.Div(id='Branch_output'),
            html.Div(id='Button_sel'),
            html.Div([
                dcc.Graph(id='3d-plot'),
                html.Button('Next Branch', id='next_branch-button', n_clicks=0),
                html.Button('Axon', id='Axon', n_clicks=0),
                html.Button('Basal Dendrite', id='B_Dendrite', n_clicks=0),
                html.Button('Apical Dendrite', id='A_Dendrite', n_clicks=0),
                html.Button('RESET MORPHOLOGY', id='reset', n_clicks=0),
                html.Button('NEXT FILE', id='next-file', n_clicks=0),
                dcc.Store(id='click-store', data={'next_branch_click': 0,'next_morph_click':0})
            ])
        ])

        # Callback to update the plot and handle next file
        @app.callback(
            [Output('3d-plot', 'figure'),
             Output('Branch_output', 'children'),
             Output('Button_sel', 'children'),
             Output('click-store', 'data'),
             Output('title', 'children')
            ],
            [Input('next_branch-button', 'n_clicks'),
             Input('Axon', 'n_clicks'),
             Input('B_Dendrite', 'n_clicks'),
             Input('A_Dendrite', 'n_clicks'),
             Input('reset', 'n_clicks'),
             Input('next-file', 'n_clicks')],
            [State('click-store', 'data')]
        )
        def update_plot(next_branch, axon, a_dendrite, b_dendrite, reset, next_file, click_data):
            
            button_clicked = self.button_clicked
            id_branch = click_data['next_branch_click']
            id_morph = click_data['next_morph_click']
            self.fig = self.plot_morphology()
            if button_clicked != None:
                self.color_processed_branches()

            if (button_clicked != None and "reset" == ctx.triggered_id):
                self.fig = self.reset()

            # Loop through the branches and add them to the figure

            if  "next_branch-button" == ctx.triggered_id:
                click_data['next_branch_click'] += 1
                id_branch = click_data['next_branch_click']
                point_update = self.next_branch(click_data['next_branch_click'])

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
                self.add_trace_branch(point_update,color)
                self.update_type(branch_type,id_branch)

            # Update the layout
            self.fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
            branch_info = f"Selected Branch: {id_branch}"
            if "next_branch-button" == ctx.triggered_id:
                branch_type_selected = f"Branch {id_branch} selected as :"
            else:
                branch_type_selected = f"Branch {id_branch} selected as {ctx.triggered_id}"

            if 'next-file' == ctx.triggered_id:
                click_data['next_morph_click'] += 1
                id_morph = click_data['next_morph_click']
                print(id_morph)
                if self.next_file() == False:
                    sys.exit()

            return self.fig, branch_info, branch_type_selected, click_data, f'Visualizing morphology n. {self.n_morph}'

        # Run the server
        if __name__ != '__main__':
            app.run_server(debug=True)
        
        return app

    def run(self):
        # Open browser automatically
        def open_browser(): 
            webbrowser.open_new("http://127.0.0.1:8050/")
            return
        #Method to start processing all files in the folder
        if not self.swc_files:
            print("No .swc files found in the specified folder")
            return
        #Timer(1, open_browser).start()
        app = self.initialize_app()
        return app

        