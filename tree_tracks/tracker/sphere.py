from tree_tracks.tracker import Tracker
import numpy as np
import plotly.graph_objects as go
import copy
class Sphere(Tracker):

    def __init__(self, pos, props, surf_props= {}, cdata_props= []):
        super().__init__(pos, props, surf_props, cdata_props)
        self.rad_prop = 'R200m'
        self.setMarkerCompatible(False)
        return

    
    def _get_sphere(self, x, y, z, radius, resolution = 20):
        u, v = np.mgrid[0:2*np.pi:resolution*2j, 0:np.pi:resolution*1j]
        X = radius * np.cos(u)*np.sin(v) + x
        Y = radius * np.sin(u)*np.sin(v) + y
        Z = radius * np.cos(v) + z
        return (X, Y, Z)
    
    def setRad(self, rad_prop:str):
        self.rad_prop = rad_prop
        return
    
    def getEmptyTrace(self):
        return go.Surface()
    
    def getAxes(self, snap_slc = slice(None)):
        pos = self.getPos(snap_slc)
        if len(pos) == 0:
            return 0, 0
        
        pos = pos[-1, :]
        rad = self.getProp(self.rad_prop, snap_slc)[-1]

        return pos - rad, pos + rad
    
    def plot(self, snap_slc = None):
        
        # by default, this will plot only the most recent radius

        if not self.dim == 3:
            raise ValueError("sphere tracker not defined for non 3D plots")
        snap_slc = self._default_snap(snap_slc)

        custom_list = self._getTraceCustomList(snap_slc)

        rad_arr = self.getProp(self.rad_prop, snap_slc)
        
        pos = self.getPos(snap_slc)
        plot_kw = copy.deepcopy(self.plot_args)
        if custom_list:
            plot_kw['customdata'] = np.stack(custom_list, axis = -1)
        
        if len(rad_arr) == 0:
            return go.Surface(**plot_kw)
        
        else:
            lpos = pos[-1, :]
            rad = rad_arr[-1]
            X, Y, Z = self._get_sphere(lpos[0], lpos[1], lpos[2], rad)
            plot_kw['x'] = X; plot_kw['y'] = Y; plot_kw['z'] = Z
            return go.Surface(**plot_kw)
        