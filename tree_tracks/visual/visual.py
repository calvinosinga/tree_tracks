#!usr/bin/python3

from typing import List, Dict, Callable, Union # to handle deprecated behavior
import plotly.graph_objects as go
from tree_tracks.tracker.tracker_super import Tracker
from tree_tracks.decorator import Decorator
import numpy as np
from abc import abstractclassmethod

class Visual(object):
    """
    A class that handles interactions between trackers and 
    plotly figure objects, updating the plotly tracer
    objects that each figure object has according to the
    function called.

    """
    def __init__(self, trackers : List[Tracker] = []):
        self.trackers = trackers
        return
    
    def includeData(self, props : Union[List[str], str]):
        if isinstance(props, str):
            for trk in self.trackers:
                trk.setCustom([props])
        else:
            for trk in self.trackers:
                trk.setCustom(props)
        return
    
    def getDataIdx(self, prop_name : str) -> int:
        return self.trackers[0].getCustomIdx(prop_name)
    
    @abstractclassmethod
    def _updateFrames(cls, fig, selector, update_dict):
        for frame in fig.frames:
            for trace in frame.data:
                if selector(trace):
                    trace.update(update_dict)
        return
    
    def setColormap(self, fig : go.Figure, col_prop : str, 
                  cmap_list : List, cmin : float = None,
                  cmax : float = None, 
                  cbar_props : Dict = {}):
        # if just Figure, not an animation
        if not len(self.trackers) == len(cmap_list):
            msg = "elements in given color list and number of trackers" + \
                "do not match"
            raise ValueError(msg)

        for i in range(len(self.trackers)):
            # get unique prop for selector in update traces
            trk = self.trackers[i]
            index = trk.getProp("index") # returns (nsnaps,) array
            index = index[0] # index should be the same for each elm
            
            # get index of that property in custom data
            cdata_idx = trk.getCustomIdx("index")

            # create selector function
            def _selector(trace):
                if trace.customdata is None:
                    return False
                if len(trace.customdata) <= cdata_idx:
                    return False
                trace_val = trace.customdata[cdata_idx][0]
                res = index == trace_val
                return res
            
            cmap = cmap_list[i]                
            colors = trk.getProp(col_prop, trk.getAlive())
            
            line_dict = {'color':colors, 'colorscale':cmap}
            fsnap = np.inf
            for ii in range(len(self.trackers)):
                is_alive_fidx = np.where(self.trackers[ii].getAlive())[0][0]

                if is_alive_fidx < fsnap:
                    fsnap = is_alive_fidx
                    fsnap_idx = ii
                
            if cmin is not None and cmax is not None:
                line_dict['cmin'] = cmin
                line_dict['cmax'] = cmax
                
                # find the tracker that is alive the earliest -
                # for animations
                 
                if i == fsnap_idx:
                    line_dict['showscale'] = True
                    if cbar_props:
                        line_dict['colorbar'] = cbar_props

            # if figure is not an animation, update normally
            if not fig.frames:
                fig.update_traces(
                    selector = _selector,
                    line = line_dict
                )
            
            # if fig is an animation, use helper method
            # to update each frame
            else:
                self._updateFrames(fig, _selector, {'line':line_dict})
        
        return
    
    
    def setColor(self, fig : go.Figure, 
                     f : Callable[[Tracker], str]):
        for i in range(len(self.trackers)):
            trk = self.trackers[i]
            index = trk.getProp("index")[0]
            
            cdata_idx = trk.getCustomIdx("index")

            color = f(trk)

            # create selector function
            def _selector(trace):
                if trace.customdata is None:
                    return False
                if len(trace.customdata) <= cdata_idx:
                    return False
                trace_val = trace.customdata[cdata_idx][0]
                return index == trace_val

            # test if animation
            if not fig.frames:
                fig.update_traces(
                    selector = _selector,
                    line_color = color
                )
            else:
                udict = {'line_color' : color}
                self._updateFrames(fig, _selector, udict)
        return
    
    def setName(self, fig : go.Figure, name_prop : str = '', 
                name_list : List[str] = []):
        if name_list:
            if not len(self.trackers) == len(name_list):
                msg = "number of names given and number of trackers" + \
                    "do not match"
                raise ValueError(msg)
            
        for i in range(len(self.trackers)):
            # get unique prop for selector in update traces
            trk = self.trackers[i]
            index = trk.getProp("index")[0]
            
            # get index of that property in custom data
            cdata_idx = trk.getCustomIdx("index")

            # create selector function
            def _selector(trace):
                if trace.customdata is None:
                    return False
                if len(trace.customdata) <= cdata_idx:
                    return False
                trace_val = trace.customdata[cdata_idx][0]
                return index == trace_val
            
            # if name list is not empty
            if name_list:
                name = name_list[i]
            else:
                # assumes that the values for this property
                # are the same throughout
                name = trk.getProp(name_prop, snap_slc = 0)
            if not isinstance(name, str):
                name = str(name)
            if not fig.frames:
                fig.update_traces(selector = _selector, name = name)
            else:
                self._updateFrames(fig, _selector, {'name' : name})
        return

    def setHover(self, fig : go.Figure, text_props : Dict[str, str] = {}):
    
        # iterate over each tracker
        for i in range(len(self.trackers)):
            trk = self.trackers[i]
            index = trk.getProp("index")[0]
            
            # get index of that property in custom data
            cdata_idx = trk.getCustomIdx("index")

            # create selector function
            def _selector(trace):
                if trace.customdata is None:
                    return False
                if len(trace.customdata) <= cdata_idx:
                    return False
                trace_val = trace.customdata[cdata_idx][0]
                return index == trace_val
            

           # iterate over each property desired in hover
           # the desired string formatting is given
            text_list = []
            for name, form in text_props.items():
                text_list.append("%s: %s"%(name, form))
            text = '<br>'.join(text_list)

            if not fig.frames:
                fig.update_traces(selector= _selector, hovertemplate = text)
            else:
                udict = {'hovertemplate': text}
                self._updateFrames(fig, _selector, udict)
        return
    