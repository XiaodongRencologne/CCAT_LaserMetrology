# %%
import numpy as np
import matplotlib.pyplot as plt
import copy

import pyvista as pv
#pv.set_jupyter_backend('trame')
#pv.set_jupyter_backend(None) 
#pv.set_jupyter_backend('server')
#pv.set_jupyter_backend('static')

from coordinate import global_coord
from rim import elliptical_rim,rect_rim
from surface import PolySurf
from Vectorpy import vector


p=pv.Plotter()

# %%
class Geo:
    """
    Generalized optical element class for 3D visualization.
    """
    def __init__(self,
                 surface,
                 rim,
                 coord_sys = global_coord, 
                 name="Geo"):
        """
        Initialize the Geo object.
        :param surface: Surface object defining the geometry.
        :param rim: Rim object defining the boundary.
        :param coord_sys: Coordinate system object.
        :param name: Name of the Geo object (optional).
        """
        self.surf=surface
        self.rim=rim
        self.coord=coord_sys
        self.name = name

        # Visualization attributes
        self.View_window = None
        self.Model_3D = None
        
        # Coordinate expressions
        self.points=vector()
        self.r_points=vector()
        self.g_points=vector()
        self.normal_v=vector()
        self.normal_v_g=vector()

    def sampling(self, Nx, Ny):
        """
        Sample the surface and calculate properties.
        :param Nx: Number of samples along the x-axis.
        :param Ny: Number of samples along the y-axis.
        """
        points = vector()
        # Sampling the surface of the model uses the method provide by rim.
        points.x, points.y, w = self.rim.sampling(Nx, Ny)

        # Calculate surface in z
        points.z = self.surf.surface(points.x, points.y)
        '''
        # Convert to global coordinates
        self.g_points.x, self.g_points.y, self.g_points.z = self.coord.Local_to_Global(
            self.points.x, self.points.y, self.points.z,
            Vector=False
        )
        '''
        # Calculate surface normal vectors
        normal_v.x, normal_v.y, normal_v.z, N_n = self.surf.normal_vector(
            points.x, points.y
        )
        '''
        # Convert normal vector to global coordinate system
        self.g_normal_v = copy.copy(self.normal_v)
        self.g_normal_v.x, self.g_normal_v.y, self.g_normal_v.z = self.coord.Local_to_Global(
            self.normal_v.x, self.normal_v.y, self.normal_v.z,
            Vector=True
        )
        '''
    
    def to_coord(self,tar_coord):
        points_new=vector()
        points_new.x,points_new.y,points_new.z=tar_coord.Global_to_local(self.g_points.x,self.g_points.y,self.g_points.z)
        return points_new
    
    def vector_rotation(self,tar_coord):
        Nvector=copy.copy(self.normal_v)
        xyz=np.append([self.normal_v.x,self.normal_v.y],[self.normal_v.z],axis=0)
        xyz=np.matmul(tar_coord.mat_g_l,xyz)
        Nvector.x=xyz[0,:]
        Nvector.y=xyz[1,:]
        Nvector.z=xyz[2,:]
        return Nvector
    
    # following the view model
    def create_model(self,
                     sampling_resolution=(50, 50)
                     ):
        x,y,w=self.rim.sampling(sampling_resolution[0],
                                sampling_resolution[1])
        del(w)
        z=self.surf.surface(x,y)
        x,y,z=self.coord.Local_to_Global(x,y,z)
        points = np.c_[x.reshape(-1), y.reshape(-1), z.reshape(-1)]
        del(x,y,z)
        cloud = pv.PolyData(points)
        self.View_3D = cloud.delaunay_2d()
        del(points)

    def view(self, widget,
             sampling_resolution=(50, 50),
             color="blue",
             opacity=0.6):
        self.create_model(sampling_resolution= sampling_resolution)
        if self.name in widget.actors:
            widget.remove_actor(self.name)
        widget.add_mesh(self.View_3D,color = color,
                        opacity=opacity,
                        show_edges=True,
                        name = self.name)
    def highlight(self, widget, color="blue"):
        """
        Highlight the 3D model by changing its color.
        :param widget: PyVista Plotter object.
        :param color: Highlight color for the model.
        """
        if self.name in widget.actors:
            actor = widget.actors[self.name]
            actor.GetProperty().SetColor(pv.parse_color(color))

    def reset_highlight(self, widget):
        """
        Reset the 3D model to its default visualization.
        :param widget: PyVista Plotter object.
        """
        if self.name in widget.actors:
            actor = widget.actors[self.name]
            actor.GetProperty().SetColor(pv.parse_color(self.default_color))


# %%
class Reflector(Geo):
    '''
    Reflector, perfect conductor
    '''
    def __init__(self, 
                 surf,
                 rim,
                 coord_sys=global_coord,
                 loss=None,
                 name="Reflector"):
        """
        Initialize the Reflector object.
        :param surf: Surface object defining the geometry.
        :param rim: Rim object defining the boundary.
        :param coord_sys: Coordinate system object.
        :param loss: Loss factor (optional, e.g., for imperfect reflectors).
        :param name: Name of the Reflector object (optional).
        """
        # Initialize the parent class (Geo)
        super().__init__(surf, rim, coord_sys, name=name)

        # Reflector-specific attributes
        self.loss = loss  # Loss factor (e.g., for imperfect reflectors)

    def view(self, 
             widget, 
             sampling_resolution=(50, 50), 
             color= (184 / 255, 115 / 255, 51 / 255), 
             opacity=0.8):
        """
        Override the view method to visualize the Reflector.
        :param widget: PyVista Plotter object.
        :param sampling_resolution: Tuple (Nx, Ny) for surface sampling resolution.
        :param color: Color of the Reflector in the visualization.
        :param opacity: Opacity of the Reflector in the visualization.
        """
        super().view(widget, 
                     sampling_resolution=sampling_resolution,
                     color=color,
                     opacity=opacity)
        
class ReflectorMultiPanel():
    '''
    Reflector, perfect conductor
    '''
    def __init__(self, 
                 surf,
                 rim_list,
                 panel_names,
                 coord_sys=global_coord,
                 loss=None,
                 name="Reflector"):
        """
        Initialize the Reflector object.
        :param surf: Surface object defining the geometry.
        :param rim: Rim object defining the boundary.
        :param coord_sys: Coordinate system object.
        :param loss: Loss factor (optional, e.g., for imperfect reflectors).
        :param name: Name of the Reflector object (optional).
        """
        self.surf = surf
        self.rim_list = rim_list
        self.coord_sys = coord_sys
        self.loss = loss
        self.name = name

        # Create individual Reflector objects for each panel
        self.panels = {
            panel_names[i] : Reflector(surf=surf, rim=rim, coord_sys=coord_sys, loss=loss, name=f"{name}_Panel_{i}")
            for i, rim in enumerate(rim_list)
        }

    def sampling(self,sampling_points_list):
        """
        Perform sampling for each panel in the ReflectorMultiPanel object.
        :param sampling_points_list: List of tuples (Nx, Ny) for sampling resolution for each panel.
        """
        if len(sampling_points_list) != len(self.panels):
            raise ValueError("The length of sampling_points_list must match the number of panels.")

        for i, (panel_name, panel) in enumerate(self.panels.items()):
            Nx, Ny = sampling_points_list[i]
            panel.sampling(Nx, Ny)

    def view(self, widget, 
             sampling_resolution=(50, 50), 
             color=(184 / 255, 115 / 255, 51 / 255), 
             opacity=0.8):
        """
        Visualize all panels in the ReflectorMultiPanel object.
        :param widget: PyVista Plotter object.
        :param sampling_resolution: Tuple (Nx, Ny) for surface sampling resolution.
        :param color: Color of the Reflector panels in the visualization.
        :param opacity: Opacity of the Reflector panels in the visualization.
        """
        # Visualize each panel individually
        for panel_name, panel in self.panels.items():
            panel.view(widget, 
                       sampling_resolution=sampling_resolution, 
                       color=color, 
                       opacity=opacity)

        # Show the plotter if no external widget is provided
        if not widget.ren_win:  # Check if the widget is already displayed
            widget.show()

    def hide(self, widget):
        """
        Hide or remove all panels in the ReflectorMultiPanel object from the PyVista widget.
        :param widget: PyVista Plotter object.
        """
        for panel_name, panel in self.panels.items():
            panel.hide(widget)

    def highlight_panel(self, panel_name, widget, color="yellow"):
        """
        Highlight a specific panel by changing its color.
        :param panel_name: Name of the panel to highlight.
        :param widget: PyVista Plotter object.
        :param color: Highlight color for the panel.
        """
        if panel_name not in self.panels:
            raise ValueError(f"Panel '{panel_name}' does not exist.")

        # Highlight the specific panel
        self.panels[panel_name].highlight(widget, color=color)

    def reset_panel_highlight(self, panel_name, widget):
        """
        Reset the highlight of a specific panel to its default visualization.
        :param panel_name: Name of the panel to reset.
        :param widget: PyVista Plotter object.
        """
        if panel_name not in self.panels:
            raise ValueError(f"Panel '{panel_name}' does not exist.")

        # Reset the highlight of the specific panel
        self.panels[panel_name].reset_highlight(widget)
    