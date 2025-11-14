from .coordinate import coord_sys
from .surface import PolySurf
from .rim import Rect_rim

import json, os
import numpy as np
from importlib import resources
default_config_path = resources.files(__package__).joinpath('Antenna_confi/FYST_config.json')

class Geo():
    def __init__(self):
        pass
    def view(self):
        pass
class Antenna():
    def __init__(self,
                 config = default_config_path):
        """1. read FYST geometrical configuration json file"""

        with open(config, "r") as f:
            config_data = json.load(f)
        
        M2_config = config_data['M2']
        M1_config = config_data['M1']
        self.M2 = reflector(M2_config)
        self.M1 = reflector(M1_config)

class reflector:
    def __init__(self,
                 Reflector_Config,
                 Normal_factor = 3000):
        self.surface = PolySurf(Reflector_Config['PolySurf'], R = Normal_factor)
        self.coord_sys =  coord_sys(Reflector_Config['coor_sys']['origin'],
                                    angle = Reflector_Config['coor_sys']['rotation_angle'],
                                    axes = Reflector_Config['coor_sys']['rotation_axis'])
        
        self.panels = {panel_name: Rect_panel(Reflector_Config['panels'][panel_name],
                                              self.coord_sys,self.surface,
                                              Reflector_Config['adjuster_config']['p'],
                                              Reflector_Config['adjuster_config']['q']) for panel_name in Reflector_Config['panels']}

class Rect_panel:
    def __init__(self,
                 panel_config,
                 coord_sys,
                 surface,
                 p,q):
        # p, q are the panel vertical adjuster position, the distance of the adjuster to the panel center along x and y axis.
        self.p =p
        self.q =q
        self.center = panel_config[0:2]
        self.size = panel_config[2:]
        self.rim = Rect_rim(self.center,
                            self.size[0],
                            self.size[1])
        self.corners = np.array([[self.center[0]-self.size[0]/2,self.center[1]-self.size[1]/2],
                                 [self.center[0]-self.size[0]/2,self.center[1]+self.size[1]/2],
                                 [self.center[0]+self.size[0]/2,self.center[1]+self.size[1]/2],
                                 [self.center[0]+self.size[0]/2,self.center[1]-self.size[1]/2]])
        self.coord_sys = coord_sys
        self.surface = surface
    

    def _compensate_offset(self,
                          Meas_data,
                          Offset=0):
        '''
        The compensation is done by the normal vector of each panel center
        '''
        nx,ny,nz,N = self.surface.normal_vector(self.center[0],self.center[1])
        Offset_vector = Offset*np.array([-nx,-ny,-nz])
        Corrected_data = Meas_data - Offset_vector
        return Corrected_data
    
    def To_adjuster_position_Method1(self,
                        Meas_data,
                        Offset=0):
        p = self.p
        q = self.q
        corrected_data = self._compensate_offset(Meas_data, Offset)
        x,y,z = corrected_data[:,0],corrected_data[:,1],corrected_data[:,2]# measured surface after removing the target offset.

        z0 = self.surface.surface(x.ravel(),y.ravel()) # ideal surface
        nx,ny,nz,N = self.surface.normal_vector(self.center[0],self.center[1])
        #dz = z.ravel() - z0.ravel()
        dr = (z.ravel() - z0.ravel())*np.abs(nz)
        #print(dr*1000)
        x = x - self.center[0]
        y = y - self.center[1]

        A = np.column_stack([
            np.ones_like(x),
            x,
            y,
            x*y,
            x**2+y**2,
            ])
        coeffs = np.linalg.solve(A,dr)
        a, b, c, d, e = coeffs
        
        v1 = a - b * p + c * q - d * p * q + e * (p**2 + q**2)
        v2 = a - b * p - c * q + d * p * q + e * (p**2 + q**2)
        v3 = a + b * p + c * q + d * p * q + e * (p**2 + q**2)
        v4 = a + b * p - c * q - d * p * q + e * (p**2 + q**2)
        v5 = a
        print(v1*1000,v2*1000,v3*1000,v4*1000,v5*1000)
        return a, b,c,d,e
    
    def To_adjuster_position_Method2(self,
                                     Meas_data,
                                     Offset = 0):
        p = self.p
        q = self.q

        self.surface._create_offset_surface(Offset)

        z0 = self.surface.surface_offset(Meas_data[:,0].ravel(),Meas_data[:,1].ravel(),grid = False)
        nx,ny,nz,N = self.surface.normal_vector(self.center[0],self.center[1])
        dr = (Meas_data[:,2].ravel() - z0.ravel())*np.abs(nz)

        #center = np.array([self.center[0],self.center[1],self.surface.surface(self.center[0],self.center[1])])
        x = Meas_data[:,0] - (self.center[0]-Offset*nx)
        y = Meas_data[:,1] - (self.center[1]-Offset*ny)

        A = np.column_stack([
            np.ones_like(x),
            x,
            y,
            x*y,
            x**2+y**2,
            ])
        coeffs = np.linalg.solve(A,dr)
        a, b, c, d, e = coeffs
        
        v1 = a - b * p + c * q - d * p * q + e * (p**2 + q**2)
        v2 = a - b * p - c * q + d * p * q + e * (p**2 + q**2)
        v3 = a + b * p + c * q + d * p * q + e * (p**2 + q**2)
        v4 = a + b * p - c * q - d * p * q + e * (p**2 + q**2)
        v5 = a
        print(v1*1000,v2*1000,v3*1000,v4*1000,v5*1000)
        return a, b,c,d,e

