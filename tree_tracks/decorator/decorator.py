
import copy
import numpy as np
from typing import Callable, Dict, List, Type, Union, Sequence
from tree_tracks.tracker import Tracker
from plotly.basedatatypes import BaseTraceType
import plotly.graph_objects as go


# a decorator function should take a list of tracker objects, 
# and output a dictionary or a sequence of dictionaries
# that will be used as keyword arguments to the plotting
# function. If a sequence is provided, it is assumed to 
# mean to plot different datasets for different time
# snapshots. If a dictionary is provided only, it
# will be plotted for every snapshot
DECORATOR_FTYPE = Callable[[List[Tracker]], 
    Union[Dict, Sequence[Dict]]]

class Decorator(object):
    """
    The decorator class provides a way to plot supplementary
    information on the plotly figures, such as points or line
    segments to highlight particular events or relationships
    between trackers.
    
    A decorator object does three tasks:

    1. Creates a dataset to plot from a list of Tracker objects.
    
    """
    def __init__(
        self,
        f : DECORATOR_FTYPE,
        plot_args : Dict = {}
    ) -> None:
        self.f = f
        self.plot_args = plot_args
        self._is_decorated = False
        self.data = None
        self.plotly_constr = go.Scatter3d
        return
    
    def setPlotArgs(
        self,
        arg_dict : Dict = {},
        **kwargs
    ) -> None:
        arg_dict.update(kwargs)
        self.plot_args.update(arg_dict)
        return
    
    def setPlotFunc(
        self,
        plotly_constr : Type[BaseTraceType]
    ) -> None:
        self.plotly_constr = plotly_constr
        return
    
    def decorate(
        self,
        trackers : List[Tracker]
    ) -> None:
        # some trackers need to be excluded from
        # decoration
        tmp = []
        for trk in trackers:
            if trk.getMarkerCompatible():
                tmp.append(trk)

        if tmp:
            self.data = self.f(tmp)
            
            self._is_decorated = True

        return
    
    def getEmptyTrace(self) -> BaseTraceType:
        """
        Construct an empty plotly trace graph object. This is
        needed because when instantiating a plotly figure, 
        it's important to provide the correct number of traces
        to initialize an animation. The empty traces do not
        correspond to any visual component in the resulting
        plots.

        Returns:
            BaseTraceType: An empty graph object from plotly,
                the exact type dependent on the constructor
                given.
        """
        return self.plotly_constr()

    def plot(
        self,
        snap : int = -1
    ) -> BaseTraceType:
        # if decorate was never called, return empty trace
        if self.data is None:
            return self.getEmptyTrace()
        # if data is empty, return empty trace
        elif not self.data:
            return self.getEmptyTrace()
        # otherwise, make plot
        else:
            # organize the plotting function's arguments
            pltkwargs = {}
            pltkwargs = copy.deepcopy(self.plot_args)

            # if data is a dictionary, intended for use
            # on every snapshot.
            if isinstance(self.data, dict):

                pltkwargs.update(self.data)
                return self.plotly_constr(**self.data)
            # if snapshot not provided, default to last
            # snapshot
            elif snap == -1:
                pltkwargs.update(self.data[-1])
                return self.plotly_constr(**self.data)
            # otherwise, plot given snapshot
            else:
                pltkwargs.update(self.data[snap])
                return self.plotly_constr(**self.data)

    def decoratePlot(
        self,
        trackers : List[Tracker],
        snap : int
    ) -> BaseTraceType:
        if self._is_decorated:
            return self.plot(snap)
        else:
            self.decorate(trackers)
            return self.plot(snap)
    
