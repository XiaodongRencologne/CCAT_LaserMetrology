### Tools to process Laser Metrology Measured surface
In the package, FYST_Antenna.Antenna is the pre-defined FYST geometry model.
* 1. FYST is made of reflectors (M2 and M1) that are defined by the class of **FYST_Antenna.reflector()**.
* 2. M2 and M1 are made of panels, class of **FYST_Antenna.Rect_panel()**.
* 3. The configuration of the FYST model is wroten the FILE 'Antenna_confi/FYST_config.json'
<details>
<summary>Click to expand JSON structure</summary>

```json
{
    "M2": {
        "panels": {
            "12391": [2804.8,-1423.4,700,710],
            "12491": [2804.8,-712.2,700,710],
        }
        "PolySurf": [[]],
        "coor_sys": {
            "origin": [0,-4800,0],
            "rotation_angle": [-1.2490457723982542,0,0],
            "rotation_axis": "xyz"
        },
    },
    "M1": {
        "panels": {
            "11211": [2684.8,-2218.6,670,750],
            "11311": [2684.8,-1467.4,670,750]},
        "PolySurf": [[]],
        "coor_sys": {
            "origin": [0,-4800,0],
            "rotation_angle": [-1.2490457723982542,0,0],
            "rotation_axis": "xyz"
        },
    }
}
</details>          


```python
## FYST model is pre-defined.
import numpy as np  
from LaserMetrology import Antenna
FYST = Antenna()
```

Define the coordinate system in which the surface points measured by the laser metrology system are expressed.

**LaserMetrology.coordinate.coor_sys** is a class that defines a coordinate frame by specifying a reference coordinate system, the origin of the frame expressed in the reference system, the rotation angles relative to the reference system, and the rotation-axis order (e.g., ‘xyz’). The default reference coord system is pre-defined 'global_coord' in the figure.
![image info](pictures/FYST_optics.png)


```python
from LaserMetrology.coordinate import coord_sys,global_coord
Meas_coord = coord_sys([0,0,0],
                       angle = [0,0,0],
                       axes='xyz',
                       ref_coord=global_coord)
```

1. Convert the measured surface into the coordinates expressed in M1 and M2's local coordinate systems.


```python
# Measured M2 panel '12281' in the Meas_coord frame
M2_meas = {'12281':np.array([[ 1805.07796427,-5207.13684982, 1788.41834598],
                             [ 1793.96487916,-5372.33687976, 2374.19028029],
                             [ 2396.39362041,-5178.44001078, 1805.02259883],
                             [ 2389.45361938,-5340.70902757, 2381.53839599],
                             [ 2095.1812338, -5274.63576201, 2078.41438517]])}

# convert the measured M2 panel points into M2's local coordinate system
M2_meas_local = {key: np.column_stack([Meas_coord.To_coord_sys(FYST.M2.coord_sys,
                                              M2_meas[key][:,0],
                                              M2_meas[key][:,1],
                                              M2_meas[key][:,2])]).T for key in M2_meas}
print(M2_meas_local)
```

    {'12281': array([[ 1805.07796427, -1825.39059124,   179.30360881],
           [ 1793.96487916, -2433.3434782 ,   207.81844975],
           [ 2396.39362041, -1832.06803129,   211.7785465 ],
           [ 2389.45361938, -2430.3129078 ,   240.14694309],
           [ 2095.1812338 , -2121.85002033,   206.9733178 ]])}
    

2. Each panel has five measured points, the adjuster positions can be directly determined from these five points.

* The measured surface is offset from the actual surface by 20–100 mm.


```python
## 
offset = 100 #mm
FYST.Offset_surface(offset)
M2_meas_adjusters = {key: FYST.M2.panels[key].To_adjuster_position_Method2(M2_meas_local[key]) for key in M2_meas_local}
```

    v1: 107.58318570101592um
    v2: 32.78839198628999um
    v3: 32.77258043416085um
    v4: -26.00728188621784um
    v5: 10.00073751466253um
    
