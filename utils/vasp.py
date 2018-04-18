import os, sys, shutil
import numpy as np
from utils import template



class VaspINCAR(template.ConfigTemplate):
    @classmethod
    def is_config(cls, line):
        line = line.strip()
        return line != '' and not line.startswith('#')
    @classmethod
    def parse_config(cls, line):
        line = line.strip()
        arg, _, info = line.partition('#')
        key, _, val = arg.partition('=')
        return key.strip(), val.strip(), info.strip()
    @classmethod
    def make_config(cls, key, val, info):
        line = ' = '.join([key, val])
        if info != '':
            line = '\t\t# '.join([line, info])
        line = ''.join([line, '\n'])
        return line
    @classmethod
    def disable_line(cls, line):
        line = ''.join(['#', line])
        return line



def parse_matrix_inblock(blocklines, matsep='--', elesep=' ', dtype=float):
    mat_raw = ''.join(blocklines).split(matsep)
    mat_raw = [s.strip() for s in mat_raw if s.strip()][1]
    mat_raw = [s.strip() for s in mat_raw.splitlines()]
    mat = np.fromstring(elesep.join(mat_raw), dtype=dtype, sep=elesep)
    mat = mat.reshape(len(mat_raw), -1)
    return mat



def parse_outcar(carpath, magnetic=False):

    with open(carpath, 'r') as file:
        flines = file.readlines()

    result = {}
    # space group, number of unique kpoints
    for line in flines:
        line = line.strip()
        if 'full space group' in line:
            result['spacegroup'] = line.rstrip(' .').split()[-1]
        if 'irreducible k-points:' in line:
            result['uniquekpoints'] = int(line.split()[1])
            break
    # total energy
    for line in flines[::-1]:
        line = line.strip()
        if line.startswith('free  energy   TOTEN'):
            result['energy'] = float(line.split()[-2])
            break   
    # number of iterations
    for line in flines[::-1]:
        line = line.strip()
        if '- Iteration ' in line:
            line = line.strip('-')
            result['niter'] = int(line.split()[1].strip('()'))
            break
    # magnetization on each atom
    if magnetic:
        for i, line in enumerate(flines[::-1]):
            line = line.strip()
            if line.startswith('magnetization (z)'):
                cursor_z = len(flines) - i - 1
            if line.startswith('magnetization (y)'):
                cursor_y = len(flines) - i - 1
            if line.startswith('magnetization (x)'):
                cursor_x = len(flines) - i - 1
                break
        stride = cursor_y - cursor_x
        result['magx'] = parse_matrix_inblock(flines[cursor_x:cursor_x+stride])[:,-1]
        result['magy'] = parse_matrix_inblock(flines[cursor_y:cursor_y+stride])[:,-1]
        result['magz'] = parse_matrix_inblock(flines[cursor_z:cursor_z+stride])[:,-1]

    return result