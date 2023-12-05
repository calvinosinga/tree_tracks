#!usr/bin/python3

from tree_tracks.tracker import Trajectory, Sphere
from tree_tracks.storage.simulation import Simulation
from typing import Dict, Callable
import numpy as np

class Vines(object):
    """
    A data storage object intended to conveniently create trackers
    for dynamic tracers centered around hosts.
    """

    # default global values for needed keys
    POS_KEY = 'tjy_x'
    TCR_FIRST_KEY = 'sho_tjy_first'
    TCR_N_KEY = 'sho_tjy_last'
    HOST_RAD_KEY = 'R200m'

    def __init__(self, tcrs : Dict, halos : Dict, sim : Dict):
        """
        Instantiates 

        Args:
            tcrs (Dict): _description_
            halos (Dict): _description_
            sim (Dict): _description_
        """
        self.setTracers(tcrs) # tracer data, shape (nptls, nsnaps)
        self.setHalos(halos) # halo data
        self.setSim(sim)
        self.track_const = Trajectory
        return
    
    
    def setTracers(self, tcrs : Dict):
        if self.POS_KEY not in tcrs:
            msg = 'did not find positions under ' + \
                             'expected key'
            raise ValueError(msg)
        self.tcrs = tcrs
        return
    
    def setSim(self, sim : Simulation):
        # properties that are true everywhere in the box for all halos
        self.sim = sim
        return
    
    def setTracker(self, const : Callable):
        self.track_const = const
        return
    
    def setHalos(self, halos : Dict):
        self.halos = halos
        return
    

    def getAlive(self, ptl_idx):
        pos = self.getPos(ptl_idx)
        not_alive = np.all(pos == -1, axis = 1)
        return ~not_alive
    
    def getIdx(self, halo_id):
        return np.where(halo_id == self.halos)[0]
    
    def getHaloPtls(self, halo_idx):
        ftcr = self.halos[self.TCR_FIRST_KEY][halo_idx]
        ltcr = self.halos[self.TCR_N_KEY][halo_idx] + ftcr
        mask = np.zeros(self.getNptls(), dtype = bool)
        mask[ftcr:ltcr] = True
        return np.where(mask)[0]
    
    def getPos(self, ptl_idx):
        return self.tcrs[self.POS_KEY][ptl_idx]

    def getNptls(self):
        key = list(self.tcrs.keys())[0]
        return len(self.tcrs[key])
    
    def get(self, prop = None, ptl_slc = slice(None), snap_slc = slice(None)):
        if prop is None:
            prop = list(self.tcrs.keys())
        if isinstance(prop, list):
            return {key : self.tcrs[key][ptl_slc, snap_slc] for key in prop}
        else:
            return self.tcrs[prop][ptl_slc, snap_slc]
    
    def getHaloData(self, prop = None, halo_slc = slice(None), snap_slc = slice(None)):
        # self.halos is a numpy structure array, so if no prop is specified then
        # just return all props

        # TODO handle nonexistant prop given
        if prop is None:
            return self.halos[halo_slc, snap_slc]
        else:
            return self.halos[prop][halo_slc, snap_slc]
    
    def createTrack(self, ptl_idx):
        pos = np.copy(self.getPos(ptl_idx))

        sim_dict = self.sim.getDefaults()

        prop_dict = self.get(ptl_slc = ptl_idx)
        
        prop_dict.update(sim_dict)

        nsnaps = self.sim.getSnaps()
        prop_dict['index'] = np.zeros((nsnaps), dtype=int) + ptl_idx

        is_alive = self.getAlive(ptl_idx)
        pos[~is_alive, :] = np.nan
        return self.track_const(pos, prop_dict)

    
    def createHaloTracks(self, halo_idx, include_func = None):

        # get the particles that belong to this halo
        ptl_idxs = self.getHaloPtls(halo_idx)
        
        trackers = []
        for idx in ptl_idxs:
            if include_func is not None:
                is_alive = self.getAlive(idx)
                is_included = include_func(self.get(ptl_slc = idx,
                                             snap_slc=is_alive))
            else:
                is_included = True
            
            if is_included:
                trk = self.createTrack(idx)
                trackers.append(trk)

        return trackers

    def createHostSphere(self, halo_idx):
        host_rad = self.getHaloData(self.HOST_RAD_KEY, halo_idx)
        pos = np.zeros((host_rad.shape[0], 3))
        sphere_props = {
            'R200m': host_rad,
            'index' : np.ones_like(host_rad)*halo_idx
        }
        sphere = Sphere(pos, sphere_props)
        return sphere