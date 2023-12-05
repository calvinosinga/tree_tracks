#!usr/bin/python3
from typing import Sequence, List
import numpy as np
from tree_tracks.storage import Simulation, Storage
from tree_tracks.tracker import Trajectory
from tree_tracks.tracker.tracker_super import Tracker


class Bush(Storage):
    """
    Data storage object intended for conveniently making trackers
    for particles within a particular region of the box
    
    """
    # default global values for needed keys in bush dict.
    # These should have 'KEY' in their names
    
    RAD_KEY = 'R200m'


    def __init__(self, bush : np.ndarray, sim : Simulation) -> None:
        super().__init__(bush, sim, Trajectory)
        return

    def makeTrackerList(
        self,
        idx_list : Sequence[int]
    ) -> List[Tracker]:
        
        
        trackers = []
        for idx in idx_list:
            trackers.append(self.createTrack(idx))
        
        return trackers
    

    def trackerBox(
        self,
        center : np.ndarray,
        side_length : float,
        snap_count : int
    ) -> List[Tracker]:
        
        pos = self.get(self.POS_KEY)
        pos = self._setPosNan(pos)
        dif = np.abs(pos[:, :, :] - center[:, np.newaxis, :])
        in_side_mask = dif <= side_length / 2
        in_box_mask = np.all(in_side_mask, axis = 2)
        in_box_count = np.sum(in_box_mask, axis = 0)

        idxs = np.where(in_box_count >= snap_count)[0]

        return self.makeTrackerList(idxs)
        

        