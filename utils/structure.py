import numpy as np
from utils import vasp



class MonoLayerCrI3:

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

    def write_poscar_abs(self, outpath):
        carlines = vasp.VaspPOSCAR.create(
                        self.symbols, self.numbers, 
                        self.cell, self.cartesian,
                        scale=1.0, direct=False, 
                        header='monolayer_CrI3')
        with open(outpath, 'w') as file:
            file.writelines(carlines)
        return carlines

    def write_poscar_rel(self, outpath):
        carlines = vasp.VaspPOSCAR.create(
                        self.symbols, self.numbers, 
                        self.cell/self.a, self.direct,
                        scale=self.a, direct=True, 
                        header='monolayer_CrI3')
        with open(outpath, 'w') as file:
            file.writelines(carlines)
        return carlines