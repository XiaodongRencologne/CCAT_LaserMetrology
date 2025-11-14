# %%
import os
import re

import numpy as np
import scipy
from scipy import interpolate
import matplotlib.pyplot as plt

# %%
def W_surf(x0, x1, y0, y1, Nx, Ny, z_xy, filename):
    '''create a spline surface file!!!'''
    header='x,  '+str(x0)+', ' + str(x1)+'\n'\
           + 'Nx, '+str(Nx)+'\n'\
           + 'y,  '+str(y0)+', ' + str(y1)+'\n'\
           + 'Ny, '+str(Ny)
    
    if z_xy.size==Nx*Ny:
        np.savetxt(filename+'.surf', z_xy.ravel(), header= header, delimiter=',')
        return True
    else:
        print('points number does not agree with each other!')
        return False

def R_surf(surf_file):
    with open(surf_file,'r') as f:
        line=f.readline()
        string=re.split(',| |:',line.replace(" ", ""))
        x0=float(string[1])
        x1=float(string[2])

        line=f.readline()
        string=re.split(',| |:',line.replace(" ", ""))
        Nx=int(string[1])

        line=f.readline()
        string=re.split(',| |:',line.replace(" ", ""))
        y0=float(string[1])
        y1=float(string[2])

        line=f.readline()
        string=re.split(',| |:',line.replace(" ", ""))
        Ny=int(string[1]) 
        f.close()
    
    z=np.genfromtxt(surf_file,delimiter=',',skip_header=4)

    return x0, x1, Nx, y0, y1, Ny, z

# %%
class PolySurf():
    '''
    Define a surface described by 2-D polynomials.
    
    2-D surface is defined by the polynomials: 
    
      p(x,y) = SUM_ij c_ij * (x/R)^i * (y/R)^j, 
    
    *coefficients are represented by C_ij matrix
    *R is the normalization factor.

    '''
    def __init__(self, coefficients, R=3000,  name = 'PolySurf.surf'):
        self.name = name
        self.R=R
        if isinstance(coefficients,np.ndarray) or isinstance(coefficients, list):
            self.coefficients=np.array(coefficients)
        elif isinstance(coefficients, str):
            if coefficients.split('.')[-1].lower()=='surfc':
                self.coefficients=np.genfromtxt(coefficients,delimiter=',')
            else:
                print('Please give correct surface coefficients files!')
        else:
            print('The input coefficient list or numpy.ndarry is incorrect!')
        

    def surface(self,x,y):
        z=np.polynomial.polynomial.polyval2d(x/self.R,y/self.R,self.coefficients)
        return z

    def normal_vector(self,x,y):
        '''normal vector of the surface'''
        x = np.array(x)
        y = np.array(y)
        nz=-np.ones(x.shape)
        a=np.arange(self.coefficients.shape[0])
        c=self.coefficients*a.reshape(-1,1)
        nx=np.polynomial.polynomial.polyval2d(x/self.R,y/self.R,c[1:,:])/self.R

        a=np.arange(self.coefficients.shape[1])
        c=self.coefficients*a
        ny=np.polynomial.polynomial.polyval2d(x/self.R,y/self.R,c[:,1:])/self.R
        N=np.sqrt(nx**2+ny**2+nz**2)

        nx=nx/N
        ny=ny/N
        nz=nz/N
        '''J: Jacobian Matrix determinant. J=N'''
        return nx,ny,nz,N.ravel()
    
    def _create_offset_surface(self,Offset,Nx = 201,Ny =201):
        '''create a surface file with an offset along the normal vector direction'''
        x0=-self.R *1.1
        x1=self.R *1.1
        y0=-self.R *1.1
        y1=self.R *1.1
        x=np.linspace(x0,x1,Nx)
        y=np.linspace(y0,y1,Ny)
        X,Y=np.meshgrid(x,y) #,indexing='ij'
        Z=self.surface(X,Y)

        nx,ny,nz,N=self.normal_vector(X,Y)
        X_offset=X - Offset*nx.reshape(Ny,Nx)
        Y_offset=Y - Offset*ny.reshape(Ny,Nx)
        Z_offset=Z - Offset*nz.reshape(Ny,Nx)

        x0=-self.R
        x1=self.R
        y0=-self.R
        y1=self.R
        x=np.linspace(x0,x1,Nx)
        y=np.linspace(y0,y1,Ny)
        X,Y=np.meshgrid(x,y) #,indexing='ij'
        Z=self.surface(X,Y)

        Z_new = interpolate.griddata(np.column_stack((X_offset.ravel(),Y_offset.ravel())),
                                Z_offset.ravel(), (X, Y), method='cubic')
        self.surface_offset=interpolate.RectBivariateSpline(x,y,Z_new.reshape(Ny,Nx).T)

        test = self.surface_offset(X,Y,grid = False)-Offset - Z
        #print(self._func2d(X,Y,grid = False)-Offset - Z)
        #print(test*1000)
        #print(test.max()*1000, test.min()*1000)   
        #fig = plt.figure(figsize = (10,8))
        #plt.pcolor(X,Y,np.abs(test)*1000,)
        #plt.colorbar(label='Offset error (mm)')
        #plt.xlabel('X (mm)')
        #plt.ylabel('Y (mm)')
        #plt.title('Offset Surface Error (mm)')
        #plt.show()

# %%
class Splines_Surf():
    '''
    Define a surface described by interpolating the input surface data!
    '''
    def __init__(self,surf_file):
        x0,x1,Nx,y0,y1,Ny,z=R_surf(surf_file)
        x=np.linspace(x0,x1,Nx)
        y=np.linspace(y0,y1,Ny)
        
        self._func2d=interpolate.RectBivariateSpline(x,y,z.reshape(Ny,Nx))

    def surface(self,x,y):
        z=self._func2d(x,y,grid=False)
        return z
    
    def normal_vector(self,x,y):
        pass


