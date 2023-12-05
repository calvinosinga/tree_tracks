#!usr/bin/python3

"""
This file contains the definitions for an "Marker" object. 

#TODO: description
"""

import numpy as np
import plotly.graph_objects as go
from tree_tracks.tracker.tracker_super import Tracker

class Marker(object):

    def __init__(self, mark_func, name = '', plot_prop = {}):
        """_summary_

        Args:
            mark_func (function): A function that either takes a list
                of trackers or a single tracker instance. The type
                should be declared in function signature, but will
                default to single tracker.
            plot_prop (dict, optional): _description_. Defaults to {}.
        """
        # arg_spec = inspect.getfullargspec(mark_func)
        # annot = arg_spec.annotations[arg_spec.args[0]]
        # TODO check behavior with different types, change ftype as needed,
        # throw error if types not understood
        self.f_type = 'tracker'
        self.func = mark_func
        self.plot_props = plot_prop
        self.name = name
        return
    
    def setName(self, name):
        self.name = name
        return
    
    def getEmptyTrace(self):
        return go.Scatter3d()
    
    def setPlotProp(self, prop_name = None, prop_val = None, 
                    plot_dict = {}, **kwargs):
        """_summary_

        Args:
            prop_name (_type_, optional): _description_. Defaults to None.
            prop_val (_type_, optional): _description_. Defaults to None.
            prop_dict (dict, optional): _description_. Defaults to {}.
        """

        if prop_name is not None and prop_val is not None:
            self.plot_props[prop_name] = prop_val
        
        plot_dict.update(kwargs)
        self.plot_props.update(plot_dict)
        return
        
    
    def plot(self, trackers, snap):
        
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
        
        # remove trackers that are not compatible with markers
        tmp = []
        for trk in trackers:
            if trk.getMarkerCompatible():
                tmp.append(trk)
        trackers = tmp

        # if there are no trackers, return empty scatter plot
        if len(trackers) == 0:
            return self.getEmptyTrace()
        
        if self.f_type == 'list':
            pos, cdata = self.func(trackers, snap)
        
        elif self.f_type == 'tracker':
            cdata = []
            # handle issue out of bounds issue if no trackers
            # handle out of bounds if too many output positions
            
            pos = np.zeros((len(trackers) * 10, trackers[0].dim))
            pos[:, :] = np.nan
            pos_idx = 0
            for i in range(len(trackers)):
                out_arr, trk_cdata = self.func(trackers[i], snap)
                pos_slc = slice(pos_idx, pos_idx + out_arr.shape[0])
                pos[pos_slc, :] = out_arr
                pos_idx += out_arr.shape[0]
                cdata.append(trk_cdata)
                
        # handle nans
        nan_mask = np.isnan(pos[:, 0])
        pos = pos[~nan_mask, :]

        if cdata:
            cdata = Tracker._reshapeCustom(cdata)
            plot_kwargs = dict(
                mode = 'markers',
                marker = self.plot_props,
                customdata=np.stack(cdata, axis = -1),
                name = self.name
            )
        else:
            
            plot_kwargs = dict(
                mode = 'markers',
                marker = self.plot_props,
                name = self.name
            )
        
        scat = _dim_plot(trackers[0].dim, pos, plot_kwargs)
            
        return scat
    
