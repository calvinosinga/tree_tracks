#!usr/bin/python3

"""
This file contains the definitions for a "Trajectory" object. 

#TODO: description
"""

import plotly.graph_objects as go
from tree_tracks.tracker.tracker_super import Tracker
import numpy as np

class Trajectory(Tracker):
    """
    #TODO: write
    
    """

    def __init__(self, pos, props, line_props = {}, custom_data = []):

        super().__init__(pos, props, 
                         line_props, custom_data)
        
        return
    
    def getEmptyTrace(self):
        return go.Scatter3d()
    
    def plot(self, snap_slc = None):
        # helper function, handles whether to make 2D or 3D plot
        def _dim_plot(dim, pos, plot_kwargs):
            if dim == 2:
                plot_kwargs['x'] = pos[:, 0]
                plot_kwargs['y'] = pos[:, 1]
                scat = go.Scatter(**plot_kwargs)
            elif dim == 3:
                plot_kwargs['x'] = pos[:, 0]
                plot_kwargs['y'] = pos[:, 1]
                plot_kwargs['z'] = pos[:, 2]
                scat = go.Scatter3d(**plot_kwargs)
            return scat
        
        
        
        snap_slc = self._default_snap(snap_slc)
        
        pos = self.pos[snap_slc, :]

        custom_list = self._getTraceCustomList(snap_slc)

        plot_kwargs = dict(
            mode = 'lines',
            line = self.plot_args,
            customdata=np.stack(custom_list, axis = -1)
        )


        scat = _dim_plot(self.dim, pos, plot_kwargs)
        return scat
    
