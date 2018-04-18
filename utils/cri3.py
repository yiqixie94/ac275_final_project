import os, sys, shutil
import numpy as np


def make_hcp0001(a, vac):
    basis = np.array([
        [a, 0., 0.],
        [-a/2., a/2.*np.sqrt(3), 0],
        [0., 0., vac]])
    return basis


def make_monolayer(a, vac):
    offset = np.array([0., 0., vac/2.])
    ba, bb, _ = make_hcp0001(a, vac)
    pos = np.vstack([
        np.zeros(3), 
        ba/3. + 2.*bb/3.,
        ba/3. - np.array([0.,0.,a/8.*np.sqrt(3)]),
        bb/3. - np.array([0.,0.,a/8.*np.sqrt(3)]),
        ba/3. + bb/3. + np.array([0.,0.,a/8.*np.sqrt(3)]),
        2.*ba/3. + np.array([0.,0.,a/8.*np.sqrt(3)]),
        2.*bb/3. + np.array([0.,0.,a/8.*np.sqrt(3)]),
        2.*ba/3. + 2.*bb/3. - np.array([0.,0.,a/8.*np.sqrt(3)]),
        ])
    pos += offset.reshape(1,-1)
    return pos


def write_monolayer(a, vac, filepath='./POSCAR', floatfmt='{:>19.16f}'):
    with open(filepath, 'w') as file:
        file.write('monolayer CrI3 (R3 structure)\n')
        file.write('{:>19.16f}'.format(1.) + '\n')
        for vec in make_hcp0001(a, vac):
            file.write(''.join(['{:>23.16f}'.format(e) for e in vec])+'\n')
        file.write('{:>4s}{:>4s}\n'.format('Cr','I'))
        file.write('{:>4d}{:>4d}\n'.format(2,6))
        file.write('Cartesian\n')
        for pos in make_monolayer(a, vac):
            file.write(''.join(['{:>20.16f}'.format(e) for e in pos])+'\n')
    return filepath






