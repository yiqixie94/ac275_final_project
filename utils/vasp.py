'''
VASP File templates
Author: Yiqi Xie
Date:   May 9, 2018
'''

from utils import template
import numpy as np



class VaspBoolType(template.DataType):

    _case = {
        True: ['.TRUE.', 'T', '1'],
        False: ['.FALSE.', 'F', '0'],
    }
    _reverse = {v:k for k,vals in _case.items() for v in vals}
    @classmethod
    def istype(cls, val):
        return val in cls._reverse
    @classmethod
    def decode(cls, val):
        return cls._reverse[val]
    @classmethod
    def encode(cls, pyval, i=0):
        return cls._case[pyval][i]



class VaspINCAR(template.KVPFile):

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
            nchar = len(line)
            if nchar > 19:
                nspace = ((nchar+3)//4) * 4 - nchar
            else:
                nspace = 19 - nchar
            line = line + ' ' * nspace
            line = ' # '.join([line, info])
        line = ''.join([line, '\n'])
        return line
    @classmethod
    def mute_line(cls, line):
        line = ''.join(['#', line])
        return line



class VaspKPOINTS(template.FreeFile):

    _default = ['header', 'nk', 'mode', 'grid', 'shift']
    @classmethod
    def create(cls, grid, shift=[0,0,0], mode='A', nk=0, header='KPOINTS'):
        flines = [
            str(header).strip(), 
            str(nk), str(mode).strip(), 
            ' '.join([str(k) for k in grid]), 
            ' '.join([str(k) for k in shift])]
        for i, line in enumerate(flines):
            if not line.endswith('\n'):
                flines[i] = ''.join([line, '\n'])
        return flines
    @classmethod
    def parse(cls, flines, *args, **kwargs):
        result = {}
        rlines = []
        for line in flines:
            line = line.partition('#')[0]
            rlines.append(line.strip())
        result['header'] = rlines[0]
        result['nk'] = int(rlines[1])
        result['mode'] = rlines[2]
        result['grid'] = [int(k) for k in rlines[3].split()]
        result['shift'] = [int(k) for k in rlines[4].split()]
        return result




class VaspPOSCAR(template.FreeFile):

    _default = ['header', 
                'scale', 'cell', 
                'symbols', 'numbers', 
                'direct', 'positions', 'dynamics']
    @classmethod
    def create(cls,
               symbols, numbers, cell, positions, 
               scale=1., direct=False, dynamics=None, 
               header='POSCAR', floatfmt='{:>19.16f}'):
        flines = [str(header).strip(), floatfmt.format(scale)]
        for vec in cell:
            flines.append(' '.join([floatfmt.format(e) for e in vec]))
        flines.append(''.join(['{:>4s}'.format(s) for s in symbols]))
        flines.append(''.join(['{:>4d}'.format(n) for n in numbers]))
        flines.append('Direct' if direct else 'Cartesian')
        for pos in positions:
            flines.append(' '.join([floatfmt.format(e) for e in pos]))
        if dynamics is not None:
            flines.insert(7, 'Selective dynamics')
            for i, dyn in enumerate(dynamics):
                dyn = ' '.join([VaspBoolType.encode(b) for b in dyn])
                flines[i+9] = ' '.join([flines[i+9], dyn])
        for i, line in enumerate(flines):
            if not line.endswith('\n'):
                flines[i] = ''.join([line, '\n'])
        return flines
    @classmethod
    def parse(cls, flines, *args, **kwargs):
        result = {}
        flines_ = [line.partition('#')[0].strip() for line in flines]
        result['header'] = flines_[0]
        result['scale'] = float(flines_[1])
        cellmat = np.fromstring(' '.join(flines_[2:4]), sep=' ')
        cellmat = cellmat.reshape(3, -1)
        result['cell'] = cellmat
        result['symbols'] = flines_[5].split()
        result['numbers'] = [int(n) for n in flines_[6].split()]
        n = sum(result['numbers'])
        if flines_[7].lower().startswith('s'):
            hasdyn = True
            cursor = 8
        else:
            hasdyn = False
            cursor = 7
        result['direct'] = flines_[cursor].lower().startswith('d')
        posblock = ' '.join(flines_[cursor+1:cursor+n+1])
        posblock = VaspBoolType.unify(posblock, ' ', {'i':-1}) 
        posmat = np.fromstring(posblock, sep=' ')
        posmat = posmat.reshape(n, -1)
        result['positions'] = posmat[:,:3]
        result['dynamics'] = posmat[:,3:] if hasdyn else None
        return result



class VaspPOTCAR(template.CreatableFile):
    '''this should not allow alter
        create works as loading multiple POTCARS to concatinate
        parse only gives element names IN ORDER
    '''
    _default = ['symbols', 'titles']
    @classmethod
    def create(cls, *srcpots, **kwargs):
        flines = []
        for src in srcpots:
            with open(src, 'r') as file:
                flines += file.readlines() + ['\n','\n']
        return flines[:-2]
    @classmethod
    def parse(cls, flines, *args, **kwargs):
        result = {}
        titles, symbols = [], []
        for line in flines:
            line = line.strip()
            if line.startswith('TITEL'):
                t = line.partition('=')[-1].strip()
                s = t.split()[1]
                titles.append(t)
                symbols.append(s)
        result = {'titles':titles, 'symbols':symbols}
        return result



class VaspOUTCAR(template.Parser):

    _default = ['spacegroup', 'uniquekpoints', 'energy', 'niter', 'mag']

    def __init__(self, flines, magnetic=True):
        self.contents = self.parse(flines, magnetic)

    @classmethod
    def parse(cls, flines, magnetic=True, **kwargs):
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
            magx = cls.parse_matrix_inblock(flines[cursor_x:cursor_x+stride])[:,-1]
            magy = cls.parse_matrix_inblock(flines[cursor_y:cursor_y+stride])[:,-1]
            magz = cls.parse_matrix_inblock(flines[cursor_z:cursor_z+stride])[:,-1]
            result['mag'] = np.vstack([magx, magy, magz]).T
        return result

    @staticmethod
    def parse_matrix_inblock(blocklines, matsep='--', elesep=' '):
        mat_raw = ''.join(blocklines).split(matsep)
        mat_raw = [s.strip() for s in mat_raw if s.strip()][1]
        mat_raw = [s.strip() for s in mat_raw.splitlines()]
        mat = np.fromstring(elesep.join(mat_raw), sep=elesep)
        mat = mat.reshape(len(mat_raw), -1)
        return mat