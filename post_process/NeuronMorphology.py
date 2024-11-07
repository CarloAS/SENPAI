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

class NeuronMorphology:
    def __init__(self,file):
        self.n_morph = self.extract_morphology_number(file)
        self.data = self.load_data(file)
        self.soma = self.find_soma()
        self.leafes = self.find_leafes()
        self.first_children = self.find_first_children()
        self.branches_stack = self.set_branches()
        self.points, self.edges = self.build_morphology()

    def load_data(self, file):
        # Load morphology from .swc file
        data = np.loadtxt(file)
        
        return data
    
    def extract_morphology_number(self,filename):
        # Similar regex pattern with regex library
        match = re.search(r"_(\d+)\.swc$", filename)
        n_morph = int(match.group(1))
        return n_morph

    def find_soma(self):

        data = self.data
        soma = data[data[:, 1] == 1][0]
        
        return soma
    
    def find_leafes(self):

        data = self.data
        leafes = np.array(data[data[:, 1] == 6,0],dtype=int)
        
        return leafes
    
    def find_first_children(self):

        data = self.data
        id_soma = int(self.soma[0])
        first_children = np.array(data[data[:, 6] == id_soma, 0],dtype=int)
        
        return first_children
    
    def set_branches(self):

        leafes = self.leafes
        first_children = self.first_children
        data = self.data
        id_soma = int(self.soma[0])

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

        return branches_stack

    def build_morphology(self):

        data = self.data
        edges = [[] for i in range(3)]
        points = np.zeros((len(data),4))
        for i,point in enumerate(data):
            parent_id = int(point[6])

            if parent_id != -1:
                parent_point = data[data[:, 0] == parent_id][0]
                edges[0] += [point[2], parent_point[2], None]
                edges[1] += [point[3], parent_point[3], None]
                edges[2] += [point[4], parent_point[4], None]
            
            points[i,0] = point[0]
            points[i,1] = point[2]
            points[i,2] = point[3]
            points[i,3] = point[4]

        return points,edges

    def plot(self):

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
            fig.show()

            return