#!usr/bin/python3

"""
This file contains the definitions for a "Tree" object. 

Trees are container classes that allow for a generalized form of halo 
trees. This code was developed specifically for SPARTA and MORIA trees, 
although users can define subclasses that load other tree types but
will still interact with the rest of the code correctly.
"""

from tree_tracks.tracker import Trajectory, Tracker
from tree_tracks.storage import Simulation, Storage, TrackerConstType
from typing import Callable, List
import numpy as np


class Tree(Storage):
    """
    Tree is a subclass of storage that is intended to conveniently 
    create Trackers from halo merger tree data. The general idea is
    to provide a host halo, and this class will traverse the merger
    tree to find all of the progenitors and create Tracker objects
    for them.

    Tree expects the dataset to be a numpy structured array, with
    the shape [nsnaps, (nhalos)]. Some fields may not have the 
    second dimension, which can be handled internally.
    """

    HOST_SUB_KEY = 'parent_id_cat'
    ALIVE_KEY = 'mask_alive'
    def __init__(
        self,
        tree : np.ndarray,
        sim : Simulation,
        track_const : TrackerConstType = Trajectory
    ) -> None:
        
        super().__init__(tree, sim, track_const)
        return
    
    def setHostSubKey(self, hs_key : str) -> None:
        self.HOST_SUB_KEY = hs_key
        return
    
    def setAliveKey(self, alv_key : str) -> None:
        self.ALIVE_KEY = alv_key
        return
    
    def getProgenitors(self, halo_idx : int) -> np.ndarray:
        # the snapshots progenitor is alive for
        snap_mask = self.get(self.ALIVE_KEY, oslc = halo_idx)
        
        # array of IDs for this host
        ids = self.get(self.ID_KEY, snap_mask, halo_idx)

        # get array of host_ids
        host_ids = self.get(self.HOST_SUB_KEY)

        # create mask for the elements which are in ids
        mask = np.isin(host_ids, ids)

        # find halo indices that are subhalos 
        desc_idxs = np.any(mask, axis = 0)

        return np.where(desc_idxs)[0]

    def traverseTree(
        self,
        halo_idx : int,
        depth : int = 1, 
        include_func : Callable[[np.ndarray], bool] = None
    ) -> List[Tracker]:
                
        # create tracker object for halo
        track = self.createTrack(halo_idx)

        # create depth property 
        track.setProp('depth', np.zeros(self.tree.shape[0]))

        # add to list
        track_list = [track]
        # traverse recursively
        if depth == 0:
            # if depth is zero, stop searching tree
            # for progenitors

            return track_list
        else:
            # if depth is at least one, find progenitors

            desc_idxs = self.getProgenitors(halo_idx)
            
            
            # iterate over each progenitor
            for didx in desc_idxs:
                
                # test if progenitor meets inclusion criteria, as
                # defined by user
                if include_func is not None:
                    is_included = include_func(self.get(halo_slc = didx))
                else:
                    is_included = True
                
                # if we want to include n order progenitor, 
                # recursively get n + 1 order progenitors
                if is_included:
                    desc_track_list = self.traverseTree(didx, 
                                                       depth - 1, 
                                                       include_func)
                    # update depth of progenitor's progenitors
                    for desc_track in desc_track_list:
                        desc_track_depth = desc_track.getProp('depth')
                        desc_track_depth += 1
                        desc_track.setProp("depth", desc_track_depth)
                    
                    # update track_list with progenitors
                    track_list.extend(desc_track_list)


            return track_list



