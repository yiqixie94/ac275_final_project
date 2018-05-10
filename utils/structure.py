'''
Material structures
Author: Yiqi Xie
Date:   May 9, 2018
'''

import numpy as np

class MonoLayerCrI3:
    '''a monolayer CrI3 structure,

        INPUTS:
            a:      float, lattice constant a, in angstrum
            disp:   float, iodine displacement along z-axis, scaled by a,
            vac:    float, vacuum along z-axis, in angstrum

        ATTRIBUTES:
            a:          the same as input
            disp:       the same as input
            vac:        the same as input
            symbols:    str tuple, symbol of ions, order matters
            numbers:    int tuple, number of ions, order matters
            cell:       numpy array, basis vectors, in angstrum
            direct:     numpy array, atom positions, in lattice coordinate
            cartesian:  numpy array, atom positions, in cartesian coordinate

        INTERFACES:
            symbols
            numbers
            cell
            direct
            cartesian
    '''

    symbols = ('Cr', 'I')
    numbers = (2, 6)

    def __init__(self, a, disp=0.23, vac=20.0):
        self.a = a
        self.disp = disp
        self.vac = vac
        self.cell = np.array([
            [ a,   0,   0],
            [-a/2, a/2*np.sqrt(3), 0],      
            [ 0,   0,   vac*2], 
        ])
        rz = disp * a / vac / 2
        self.direct = np.array([
            [ 0,   0,   1/2],
            [ 1/3, 2/3, 1/2],
            [ 1/3, 0,   1/2-rz],
            [ 0,   1/3, 1/2-rz],
            [ 1/3, 1/3, 1/2+rz],
            [ 2/3, 0,   1/2+rz],
            [ 0,   2/3, 1/2+rz],
            [ 2/3, 2/3, 1/2-rz],
        ])
        self.cartesian = np.dot(self.direct, self.cell)


        