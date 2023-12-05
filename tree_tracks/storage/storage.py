#!/usr/bin/python

from tree_tracks.tracker import Trajectory, Tracker
from tree_tracks.storage.simulation import Simulation
from typing import Callable, List, Sequence, Union, Dict, Collection
from abc import abstractmethod
import numpy as np
import copy
# this type is used often, basically represents various ways of 
# indexing a numpy array
ArrIndexTypes = Union[int, slice, Sequence[int], np.ndarray]
TrackerConstType = Callable[[np.ndarray, Dict[str, np.ndarray]]]


class Storage(object):
    """
    The storage base class.

    Storage objects have three tasks.
        
        1. Manage a dataset of particles. Storage objects will
        provide methods to access and manipulate the data within
        the dataset. The dataset is assumed
        to be a dictionary of numpy arrays or a numpy structured
        array. The arrays should be 2D, with the time and object axes
        in any order, assuming that the size of each axis is
        different. Arrays can also be 1D if the two axes are of
        different sizes.
        
        2. Construct Tracker instances for specified objects. The
        kind of tracker instances can be controlled by changing the
        tracker constructor attribute. Tracker objects also often
        require custom datasets for the plotly tracers, which is
        used in plotly for iteractive components of the plots,
        like hover text. The def_props list contains the 
        properties that should be loaded into custom data
        automatically.

        3. Store information about the simulation, which is given
        by the Simulation object.

    """
    # below are the assumed keynames for various quantities
    # these should have 'KEY' in their names

    POS_KEY = 'x'
    ID_KEY = 'id'

    def __init__(
            self,
            data : Union[np.ndarray, Dict[str, np.ndarray]],
            sim : Simulation,
            track_const : TrackerConstType
    ) -> None:
        self.data = data
        self.sim = sim
        self.track_const = track_const

        self.def_props = []

        # default time and obj axis behavior, using ID array
        self._tax = None
        self._oax = None
        self.nobj = -1
        if self.ID_KEY in data:
            nsnaps = self.sim.getSnaps()
            id_shape = data[self.ID_KEY]
            for i in range(len(id_shape)):
                if id_shape[i] == nsnaps:
                    self._setTimeAx(i)
                else:
                    self._setObjAx(i)
                    self.nobj = id_shape[i]

        return
    
    ##### ACCESSING / MANIPULATING DATA #############################
    def _setTimeAx(self, ax : int) -> None:
        self._tax = ax
        return
    
    def _setObjAx(self, ax : int) -> None:
        self._oax = ax
        return
    
    def _getAllProps(self) -> List[str]:
        if isinstance(self.data, dict):
            return list(self.data.keys())
        elif isinstance(self.data, np.ndarray):
            return list(self.data.dtype.names)
    
    def _getSlc(
        self,
        tslc : ArrIndexTypes,
        oslc : ArrIndexTypes,
        shape : Sequence[int]
    ) -> tuple:
        dim = len(shape) # number of dimensions
        # the axis that has the same length as number of
        # snapshots is assumed to be the time axis
        nsnaps = self.sim.getSnaps()
        slc = None
        
        def _slcHelp(dim_size):
            if dim_size == nsnaps:
                return tslc
            elif dim_size == self.nobj:
                return oslc
            else:
                return slice(None)
        
        slc_list = []
        for i in range(dim):
            slc_list.append(_slcHelp(shape[i]))
        slc = tuple(slc_list)
            
        return slc

    def setPosKey(self, pos_key : str) -> None:
        self.POS_KEY = pos_key
        return
    
    def setIDKey(self, id_key : str) -> None:
        self.ID_KEY = id_key
        return
    
    def get(
        self,
        prop : Union[str, Sequence[str]] = '',
        tslc : ArrIndexTypes = slice(None),
        oslc : ArrIndexTypes = slice(None)
    ) -> Union[np.ndarray, Dict[str, np.ndarray]]:
        """

        Args:
            prop (Union[str, Sequence[str]], optional): _description_. Defaults to ''.
            tslc (Union[int, slice, Sequence[int], np.ndarray], optional): _description_. Defaults to slice(None).
            oslc (Union[int, slice, Sequence[int], np.ndarray], optional): _description_. Defaults to slice(None).

        Returns:
            Union[np.ndarray, Dict[str, np.ndarray]]: if prop is str,
                then is returned as array. Otherwise dictionary.
        """

        # if no props are given, assumed that all props are desired
        if prop == '':
            prop = self._getAllProps()
        
        if isinstance(prop, str):
            in_arr = self.data[prop]
            slc = self._getSlc(tslc, oslc, in_arr.shape)
            out = in_arr[slc]

        else:
            out = {}
            for p in prop:
                in_arr = self.data[p]
                slc = self._getSlc(tslc, oslc, in_arr.shape)
                out[p] = in_arr[slc]
        
        return out
    
    def idToIdx(self, obj_id : Union[int, Sequence[int]]):
        ids = self.data[self.ID_KEY]
        idxs = np.where(obj_id == ids)
        if not idxs:
            raise ValueError(f'no matches found for ID {obj_id}')
        else:
            return idxs[self._oax]
    
    def getKeynames(self) -> str:

        out = 'EXPECTED KEYNAMES'
        for var_name, var_value in vars(self.__class__).items():
            if 'KEY' in var_name:
                out+=f"{var_name}: {var_value}"
                out+='\n'
        return out

    ##### CREATING TRACKERS #########################################
    
    def createTrack(
            self,
            idx : int
    ) -> Tracker:
        
        

        pos = copy.deepcopy(self.get(self.POS_KEY, oslc = idx))
        props = copy.deepcopy(self.get(self.def_props, oslc = idx))
        nsnaps = self.sim.getSnaps()
        props['index'] = np.zeros((nsnaps), dtype = int) + idx

        # set invalid position values to np.nan instead of -1
        pos = self._setPosNan(pos)


        return self.track_const(pos, props)
    
    def _setPosNan(self, pos : np.ndarray) -> np.ndarray:
        not_alive = np.all(pos == -1, axis = 1)
        tslc = self._getSlc(not_alive, slice(None), pos.shape)
        pos[tslc] = np.nan
        return pos
    
    def setTrackConst(
        self,
        track_const : TrackerConstType
    ) -> None:
        self.track_const = track_const
        return
    
    
    def setTrackerCustom(self, props : List[str]) -> None:
        self.def_props = props
        return
    
    ##### CLASS METHODS FOR VARIOUS USEFUL FUNCTIONALITIES ##########

    @abstractmethod
    def unwrapPositions(trackers : List[Tracker], boxsize : float):
        """
        Since the positions of the trackers are logged in a periodic
        box, the positions are wrapped when they cross the boundary
        of the box. This function unwraps their positions, allowing
        for their positions to be displayed continuously

        Args:
            trackers (_type_): _description_
            boxsize (_type_): _description_
        """
        # first determine if unwrapping is necessary

        # if the range of positions is greater than L/2, then
        # unwrapping is needed
        pos_range = np.zeros((3, 2))
        pos_range[:, 0] = boxsize
        for i in range(len(trackers)):
            pos = trackers[i].getPos(trackers[i].getAlive())
            for j in range(pos_range.shape[0]):
                posmin = np.min(pos[:, j])
                posmax = np.max(pos[:, j])
                pos_range[j, 0] = min(posmin, pos_range[j, 0])
                pos_range[j, 1] = max(posmax, pos_range[j, 1])
        
        for a in range(pos_range.shape[0]):
            if pos_range[a, 1] - pos_range[a, 0] >= boxsize / 2:
                for i in range(len(trackers)):
                    pos = trackers[i].getPos(trackers[i].getAlive())
                    unwrap_mask = pos[:, a] <= boxsize / 2
                    pos[unwrap_mask, a] += boxsize
                    newpos = np.zeros((trackers[i].getAlive().shape[0], 3))
                    newpos[:, :] = np.nan
                    newpos[trackers[i].getAlive()] = pos
                    trackers[i].setPos(newpos)
                    


        return trackers
    
    @abstractmethod
    def transformCOM(trackers : List[Tracker]) -> List[Tracker]:
        """
        Given list of trackers, will find their center of mass and 
        the transform the positions of the trackers such that the
        center of mass is at the origin.

        Args:
            trackers (List[Tracker]): _description_

        Returns:
            List[Tracker]: _description_
        """
        return
    