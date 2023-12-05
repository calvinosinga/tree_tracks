#!usr/bin/python3

"""
This file contains the definitions for common marker functions
"""

from tree_tracks.tracker.tracker_super import Tracker
import numpy as np

### HELPER FUNCTIONS ################################################

def _catch_missing_prop(tracker, propname, funcname):
    try:
        val = tracker.getProp(propname)
    except KeyError:
        msg = '%s markfunc requires %s to be stored in tracker data'
        raise KeyError(msg%(propname, funcname))
    return val

def _make_nan_arr(tracker):
    arr = np.empty(tracker.dim) # matches 2D or 3D positions
    arr[:] = np.nan
    return arr

def _retrieve_custom_data(tracker, snap):

    cdata = tracker.cdata
    custom_arr = np.zeros(len(cdata))
    if cdata:
        for i in range(len(cdata)):
            tmp = tracker.getProp(cdata[i], snap)
            if isinstance(tmp, np.ndarray):
                tmp = tuple(tmp)
                custom_arr = np.zeros(len(cdata), dtype = object)

            custom_arr[i] = tmp
            
    return custom_arr

### MARKER FUNCTIONS ################################################

def birth(tracker : Tracker, snap : int):
    mask = tracker.getAlive()
    # get first true value
    birth_snap = np.argmax(mask)

    cdata = _retrieve_custom_data(tracker, snap)

    if snap >= birth_snap:
        birth_pos = tracker.getPos(birth_snap)
        return birth_pos, cdata
    else:
        return _make_nan_arr(tracker), cdata
    
def death(tracker : Tracker, snap : int):
    mask = tracker.getAlive()
    
    # get last true value
    death_snap = np.max(np.where(mask))

    is_last_snap = death_snap == tracker.dim - 1
    
    cdata = _retrieve_custom_data(tracker, snap)

    if snap >= death_snap and not is_last_snap:

        death_pos = tracker.getPos(death_snap)
        return death_pos, cdata
    
    else:
        return _make_nan_arr(tracker), cdata
    

def infall(trk : Tracker, snap : int):
    fname = 'infall'
    tinf = _catch_missing_prop(trk, 'ifl_t_infall', fname)[snap]
    snapt = _catch_missing_prop(trk, 'snap_t', fname)[snap]
    iflx = _catch_missing_prop(trk, 'ifl_x', fname)[snap]
    
    cdata = _retrieve_custom_data(trk, snap)

    if tinf <= snapt:
        return iflx, cdata
    else:
        return _make_nan_arr(trk), cdata

def pericenter(trk : Tracker, snap : int):
    fname = 'pericenter'
    had_peri = _catch_missing_prop(trk, 'oct_had_pericenter', fname)

    # get first true value
    first_snap = np.argmax(had_peri)
    
    cdata = _retrieve_custom_data(trk, snap)

    if snap >= first_snap:
        pos = trk.getPos(first_snap)
        return pos, cdata
    else:
        return _make_nan_arr(trk), cdata

