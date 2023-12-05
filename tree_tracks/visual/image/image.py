#!usr/bin/python3

"""
This file contains methods that create images following the
trajectories of a halo and its descendents

#TODO: description
"""
    
import plotly.graph_objects as go
from tree_tracks.tracker.tracker_super import Tracker
from tree_tracks.decorator import Decorator
from typing import List, Dict
from tree_tracks.visual.visual import Visual

class Image(Visual):

    def __init__(self, trackers : List[Tracker] = [],
                 decorators : List[Decorator] = [],
                 layout : Dict = {}): # update so layout can also be go.Layout object
        super().__init__(trackers)
        self.includeData(["index"])
        self.decorators = decorators
        self.layout = layout
        return
    
    def setLayout(self, layout : Dict = {}):
        self.layout.update(layout)
        return
    
    def numTrackers(self) -> int:
        return len(self.trackers)
    
    def getFig(self) -> go.Figure:
        data = []

        for i in range(len(self.trackers)):
            scat = self.trackers[i].plot()
            data.append(scat)
        
        for i in range(len(self.decorators)):
            lsnap = len(self.trackers[0].getAlive()) - 1
            scat = self.decorators[i].plot(self.trackers, lsnap)
            data.append(scat)
        fig = go.Figure(data = data, layout=self.layout)
        return fig
    



    