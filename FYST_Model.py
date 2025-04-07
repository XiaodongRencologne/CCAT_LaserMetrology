from CCAT_LaserMetrology.MM_HoloPy.coordinate import coord_sys
from surface import PolySurf
import json, os


class FYST_GEO():
    def __init__(self,
                 config = 'FYST_config.json'):
        """1. read FYST geometrical configuration json file"""
        
        config_data = json.load(config)
        M2_config = config_data['M2']
        M1_config = config_data['M1']

        """2. Define surface functions of M1 and M2 """
        self.M1_surface = PolySurf(M1_config['PolySurf'], R = 3000)
        self.M2_surface = PolySurf(M2_config['PolySurf'], R = 3000)

        """3. Define coordinate system, M2, M1, Rx, rotation frame"""

        self.M1_coor_sys = coord_sys(M1_config['coor_sys']['origin'],
                                     M1_config['coor_sys']['angle'],
                                     M1_config['coor_sys']['rotation_axis'])
        
        self.M2_coor_sys = coord_sys(M2_config['coor_sys']['origin'],
                                     M2_config['coor_sys']['angle'],
                                     M2_config['coor_sys']['rotation_axis'])  

        self.M2_panels = M2_config['panels']
        self.M1_panels = M1_config['panels']
        
        """4. M1 and M2 panel position and panel size"""
    def view(self, widget = None):
        pass