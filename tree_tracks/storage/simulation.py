#!/usr/bin/python3
import numpy as np

class Simulation(object):

    def __init__(self,
            boxsize : float, 
            time : np.ndarray
        ) -> None:
        self.box = boxsize
        self.time = time
        return

    def getSnaps(self) -> int:
        return len(self.time)
    
    def getTime(self) -> np.ndarray:
        return self.time
    
    def getBox(self) -> float:
        return self.box
