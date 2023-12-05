#!usr/bin/python3

"""
This file contains the definitions for a "Trace" object. 

#TODO: description
"""

import numpy as np
from abc import abstractmethod
import copy
from typing import List

class Tracker(object):
    """
    Tracker object stores info from a particle,
    outputs a desired plotly trace when plot(..)
    is called
    
    """

    def __init__(self, pos, props, plot_args = {}, cdata_props = []):

        self.props = Tracker._reformatProps(props)
        self.plot_args = plot_args
        self.pos = pos
        self.cdata = cdata_props
        self.dim = pos.shape[1]
        self._is_decoratable = True
        return
    
    @abstractmethod
    def _reformatProps(in_halo_props):
        if isinstance(in_halo_props, np.ndarray):
            dic = {}
            for name in in_halo_props.dtype.names:
                dic[name] = in_halo_props[name]
            return dic
        elif isinstance(in_halo_props, dict):
            return in_halo_props
        # handle other cases

    def setCustom(self, cdata_props : List[str]):
        self.cdata = cdata_props
        return
    
    def getCustomIdx(self, cdata_prop : str):
        return self.cdata.index(cdata_prop)
    
    def _getTraceCustomList(self, snap_slc):
        custom_list = []
        if self.cdata:
            for i in range(len(self.cdata)):
                tmp = self.getProp(self.cdata[i], snap_slc)
                custom_list.append(tmp)

            custom_list = Tracker._reshapeCustom(custom_list)
        return custom_list
    
    def _default_snap(self, snap_slc):
        if snap_slc is None:
            snap_slc = self.getAlive()
        else:
            # only plot overlap between desired snap_slc and
            # is alive
            is_alive = self.getAlive()
            user_snaps = np.zeros_like(is_alive)
            user_snaps[snap_slc] = True
            snap_slc = is_alive & user_snaps
        return snap_slc
    
    @abstractmethod
    def _reshapeCustom(custom_list):
        # I am assuming that the arrays are at most 2D, (nsnaps, ndim)
        
        # get shape of 1D arrays
        if custom_list[0].ndim == 1:
            shape_1d = custom_list[0].shape
        else:
            shape_1d = custom_list[0].shape[0]
        
        # reshape 2D arrays
        for arr_i, arr in enumerate(custom_list):
            if arr.ndim == 2:
                new_arr = np.zeros(shape_1d, dtype = object)
                # compose tuples
                for i in range(len(new_arr)):
                    new_arr[i] = tuple(arr[i, :])

                custom_list[arr_i] = new_arr
                

        return custom_list
    
    def setProp(self, prop_name = None, prop_val = None, prop_dict = {}):
        """_summary_

        Args:
            prop_name (_type_, optional): _description_. Defaults to None.
            prop_val (_type_, optional): _description_. Defaults to None.
            prop_dict (dict, optional): _description_. Defaults to {}.
        """
        if prop_name is not None and prop_val is not None:
            self.props[prop_name] = prop_val
        
        if prop_dict:
            self.props.update(prop_dict)
        return

    def getProp(self, prop_name, snap_slc = slice(None)):
        # TODO throw error if prop not available
        return self.props[prop_name][snap_slc]
    
    def getPos(self, snap_slc = slice(None)):
        return copy.deepcopy(self.pos[snap_slc, :])
    
    def setPos(self, new_pos):
        self.pos = new_pos
        return
    
    def getAlive(self):
        is_alive = ~np.isnan(self.pos[:, 0])
        return is_alive
    
    def setPlotArgs(self, prop_name = None, prop_val = None, 
                    prop_dict = {}, **kwargs):
        """_summary_

        Args:
            prop_name (_type_, optional): _description_. Defaults to None.
            prop_val (_type_, optional): _description_. Defaults to None.
            prop_dict (dict, optional): _description_. Defaults to {}.
        """
        if prop_name is not None and prop_val is not None:
            self.plot_args[prop_name] = prop_val
        prop_dict.update(kwargs)
        self.plot_args.update(prop_dict)
        return
    
    def getAxes(self, snap_slc = slice(None)):
        """
        Get the minimum axis ranges that will make the tracker
        visible in the plotly figure
        """
        snap_slc = self._default_snap(snap_slc)
        pos = self.getPos(snap_slc)
        return pos.min(axis = 0), pos.max(axis = 0)

    def setDecoratable(self, is_decor : bool):
        self._is_decoratable = is_decor
        return
    
    def getDecoratable(self):
        return self._is_decoratable
    
    def getEmptyTrace(self):
        pass

    def plot(self, snap_slc = None):
        pass