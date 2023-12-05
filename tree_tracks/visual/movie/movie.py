#!usr/bin/python3

"""
This file contains methods that create movies following the
trajectories of a halo and its descendents

#TODO: description
"""


# handle unit conversions
    
import plotly.graph_objects as go
import numpy as np
from tree_tracks.decorator import Decorator
from tree_tracks.tracker.tracker_super import Tracker
from tree_tracks.visual.movie.event import Event
from typing import List, Dict
from tree_tracks.visual.visual import Visual

class Movie(Visual):
    """
    Creates interactive animations using plotly. Intended for 
    jupyter notebooks. Uses plotly's internal animation code
    instead of making the animation externally.

    """
    def __init__(self, 
            trackers : List[Tracker] = [], 
            markers : List[Decorator] = [], 
            frame_duration : float = 30,
            trans_duration : float = 0
        ):
        
        super().__init__(trackers)
        self.layout = go.Layout()
        self.markers = markers

        # default button needed
        play_button = dict(
            label = "Play",
            method = 'animate',
            args = 
                [None, 
                {'frame':{'duration':frame_duration, "redraw":True},
                'transition':{'duration':trans_duration}}]
        )
        # play_button = dict(
        #     label = 'Play',
        #     method = 'animate',
        #     args = [
        #         None
        #     ]
        # )
        self.setMenu(buttons = [play_button])  
        self.setScene(
            {'aspectratio' : {'x':1, 'y':1, 'z':1}}
        )      
        return

    def setLayout(self, layout_dict):
        self.layout.update(layout_dict)
        return
    
    def setScene(self, scene_dict):
        self.layout.update(scene = scene_dict)
        return
    
    def setMenu(self, buttons : List[Dict] = [], 
                sliders : List[Dict] = []):
        
        self.layout.update(
            updatemenus = [
                dict(type = 'buttons', buttons = buttons)
                ],
            
            sliders = sliders
        )
        return
    
    def createFrames(self, snapshots):
        
        # initialize list of frames
        frames = []

        mins = np.array([np.inf] * 3)
        maxs = np.array([-np.inf] * 3)
            
        # for each snapshot
        for ss in range(len(snapshots)):
            snap_slc = slice(snapshots[0], snapshots[ss])
            frame_data = []
            
            # make plots of the trackers for this snapshot

            extant_tracks = [] # for markers later
            for trk in self.trackers: # iterate through trackers
                is_alive = trk.getAlive()
                snaps_existed = np.sum(is_alive[snap_slc])
                # if trk has existed for at least 1 snaps, make plot
                if snaps_existed >= 1:
                    extant_tracks.append(trk)
                    scat = trk.plot(snap_slc)
                    frame_data.append(scat)
                    trk_mins, trk_maxs = trk.getAxes(snap_slc)
                    mins = np.minimum(mins, trk_mins)
                    maxs = np.maximum(maxs, trk_maxs)
                else:
                    # create empty scatter plot, so plotly knows
                    # how many traces there are in the animation
                    # and to avoid artifacts at the start where
                    # traces appear and disappear.

                    empty = trk.getEmptyTrace()
                    frame_data.append(empty)

            
            # make marker plots
            
            # iterate through markers
            for mrk in self.markers:
                # give the existing tracker plots and current snap
                if extant_tracks:
                    scat = mrk.plot(extant_tracks, snapshots[ss])
                    frame_data.append(scat)
                
            
            # create traces list, from each tracker, marker
            
            # check that each frame has at least one trace
            for f in range(len(frames)):
                has_data = False
                for t in range(len(frames[f].data)):
                    if frames[f].data[t].x is not None:
                        has_data = True
                if not has_data:
                    del frames[f]
            
            if frame_data:
                frames.append(go.Frame(data = frame_data))
            
            # set default scene/annotations
        
        scene_dict = {
            'xaxis' : dict(range = (mins[0], maxs[0])),
            'yaxis' : dict(range = (mins[1], maxs[1])),
            'zaxis' : dict(range = (mins[2], maxs[2]))
        }
        for k, axis_dict in scene_dict.items():
            axis_dict['autorange'] = False
        self.setScene(scene_dict)

        # pass frames/figs to each event, which will adjust
        # scenes, annotations, or trace data as desired
        
        # set list, return copy    
        return frames
    

    def createMovie(self, frames : List[go.Frame]):
        
        fig = go.Figure(
            data = frames[0].data,
            layout = self.layout,
            frames = frames
        )
        return fig
    
    
        
class MovieExternal(Visual):
    """
    Since plotly does not have the ability
    to export its animations into gifs,
    we need to do so externally by saving
    each frame as a png and then stitching
    them together. This serves as an alternate
    to Movie in order to accomplish this.
    """

    def __init__(self, trackers: List[Tracker] = [], 
                 markers: List[Marker] = [],
                 events: List[Event] = [],
                 frame_duration: float = 30, 
                 trans_duration: float = 0):
        
        super().__init__(trackers)
        self.markers = markers
        self.events = events
        self.frame_dur = frame_duration
        self.trans_dur = trans_duration
