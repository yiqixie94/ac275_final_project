'''
Experiment formulation and manipulations at file system level
Author: Yiqi Xie
Date:   May 9, 2018
'''

import os, sys, shutil
from utils import vasp, slurm, structure


#################### General Methods ####################


class ExperimentSetMaker:
    '''manages a set of experiments in the file system, 
        typically in a form like (may be different in real cases):

            <experiment set root directory>/
                <main script>
                <meta data>
                <experiment 1>/
                    <sub script>
                    <input file 1>
                    <input file 2>
                    ...
                <experiment 2>/
                    <sub script>
                    <input file 1>
                    <input file 2>
                    ...
                ...
        
        the <sub script> instructs on how each experiment works
        the <main script> instructs on how each <sub script> is executed
    '''
    def make(self, *args, **kwargs):
        raise NotImplementedError


class ExperimentSetAnalyzer:
    '''collects the results under certain file arrangement
        remenber that if the orignal experiment set was organized as previous, 
        the output would be like (may be different in real cases):

            <experiment set root directory>/
                <main script>
                <meta data>
                <experiment 1>/
                    <sub script>
                    <input file 1>
                    <input file 2>
                    ...
                    <output file 1>
                    <output file 2>
                    ...
                <experiment 2>/
                    <sub script>
                    <input file 1>
                    <input file 2>
                    ...
                    <output file 1>
                    <output file 2>
                    ...
                ...
    '''
    def analyze(self, *args, **kwargs):
        raise NotImplementedError



class ToolKit:
    '''packaged helper functions'''

    @classmethod
    def make_out_dir(cls, out_dir, overwrite=False, merge=False):
        '''makes the output directory'''
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        elif overwrite:
            shutil.rmtree(out_dir)
            os.mkdir(out_dir)
        elif not merge:
            raise ValueError(
                'output directory \"{}\" '\
                    +'already exists.'.format(out_dir))

    @classmethod
    def copy_all(cls, src_dir, dest_dir):
        '''copies all files and subdirectories from one root to another'''
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)
        for fname in os.listdir(src_dir):
            fpath_old = os.path.join(src_dir, fname)
            fpath_new = os.path.join(dest_dir, fname)
            if os.path.isdir(fname):
                shutil.copytree(fpath_old, fpath_new)
            else:
                shutil.copy2(fpath_old, fpath_new)

    @classmethod
    def write_info(cls, out_dir, info=None):
        '''writes an info file at give directory'''
        if info is not None:
            info = str(info)
            path = os.path.join(out_dir, 'info.txt')
            with open(path, 'w') as file:
                file.write(info)

    @classmethod
    def write_poscar_abs(cls, struc, header='POSCAR', outpath='./POSCAR'):
        '''the struc should resemble the ones defined in structure.py'''
        carlines = vasp.VaspPOSCAR.create(
                        struc.symbols, struc.numbers, 
                        struc.cell, struc.cartesian,
                        scale=1.0, direct=False, 
                        header=header)
        with open(outpath, 'w') as file:
            file.writelines(carlines)
        return carlines

    @classmethod
    def write_poscar_rel(cls, struc, header='POSCAR', outpath='./POSCAR'):
        '''the struc should resemble the ones defined in structure.py'''
        carlines = vasp.VaspPOSCAR.create(
                        struc.symbols, struc.numbers, 
                        struc.cell/self.a, struc.direct,
                        scale=struc.a, direct=True, 
                        header='header')
        with open(outpath, 'w') as file:
            file.writelines(carlines)
        return carlines

    @classmethod
    def alter_file(cls, ftype, fpath, configs={}):
        '''alters a file at fpath of ftype with configs,
            the ftype should resemble the AlterableFile defined in template.py'''
        frep = ftype.load(fpath)
        flines = frep.alter(configs=configs)
        with open(fpath, 'w') as f:
            f.writelines(flines)
        return flines

    @classmethod
    def switch_template(cls, ftype, fpath, tpath, keeps=[]):
        '''switches the template of the file at fpath using the file at tpath,
            while keeping the attributes in keeps untouched.
            the ftype should resemble the AlterableFile defined in template.py'''
        frep = ftype.load(fpath)
        trep = ftype.load(tpath)
        flines = trep.alter(configs={k:frep.view(k) for k in keeps})
        with open(fpath, 'w') as f:
            f.writelines(flines)
        return flines

    @classmethod
    def continue_general(cls, exp_dir, 
                         batch_name='batch.sh', 
                         batch_update={}):
        '''safely copies the CONTCAR to be the new POSCAR
                time_update:    str, the new time setting for the job,
                                if not None, will change the batch file'''
        poscar_path = os.path.join(exp_dir, 'POSCAR')
        contcar_path = os.path.join(exp_dir, 'CONTCAR')
        shutil.copy2(poscar_path, poscar_path+'_old')
        shutil.copy2(contcar_path, poscar_path)
        cls.alter_file(
            slurm.SlurmBatchScript, 
            os.path.join(exp_dir, batch_name), 
            configs=batch_update)

    @classmethod
    def continue_relaxation(cls, exp_dir, 
                            batch_name='batch.sh', 
                            batch_update={},
                            push_conv=False):
        '''first calls continue_general(), then modify relaxation-related configs
                push_conv:      bool, whether to fix convergence issue, 
                                which is likely to be the case if the original 
                                method is conjugate gradient descent. 
                                if true, will change the INCAR to perform
                                quasi-Newton method optimization'''
        cls.continue_general(exp_dir, batch_name, batch_update)
        if push_conv:
            cls.alter_file(
                vasp.VaspINCAR, 
                os.path.join(exp_dir, 'INCAR'), 
                configs={'IBRION':'1', 'POTIM':'0.5'})





#################### Parameter Scan ####################

class ScanFromTemplate(ExperimentSetMaker):
    '''alter existing template files to make a set of experiments'''

    BATCHFILE = 'batch.sh'
    VASPINPUTS = ['INCAR', 'KPOINTS', 'POTCAR', 'POSCAR']

    def __init__(self, src_dir):
        '''src_dir contains the template files'''
        assert(os.path.isdir(src_dir))
        self.src_dir = src_dir

    def make(self, param_list, out_dir, 
             header=None, info=None, 
             overwrite=False, merge=False):
        ''' param_list: the target to scan with
            out_dir:    the root directory where the experiment set is organized
            header:     a clue str that appears in all experiment namings
            info:       an info str that would be written as '<out_dir>/info.txt'
            overwrite, merge:   the mode to make the out_dir'''
        ToolKit.make_out_dir(out_dir, overwrite, merge)
        ToolKit.write_info(out_dir, info)
        for p in param_list:
            exp_name, exp_dir = self._init_exp(out_dir, header, p)
            self._alter_vaspin(exp_dir, exp_name, p)
            self._alter_batch(exp_dir, exp_name, p)

    def _make_exp_name(self, header, p):
        '''the naming convention of each experiment'''
        raise NotImplementedError

    def _alter_vaspin(self, exp_dir, exp_name, p):
        '''the method to alter the vasp input files from given templates'''
        raise NotImplementedError

    def _alter_batch(self, exp_dir, exp_name, p):
        '''the method to alter the batch file from given template'''
        ToolKit.alter_file(
            slurm.SlurmBatchScript, 
            os.path.join(exp_dir, self.BATCHFILE), 
            configs={'--job-name':exp_name})

    def _init_exp(self, out_dir, header, p):
        exp_name = self._make_exp_name(header, p)
        exp_dir = os.path.join(out_dir, exp_name)
        ToolKit.copy_all(self.src_dir, exp_dir)
        return exp_name, exp_dir



class StrucScanFromTemplate(ScanFromTemplate):

    def __init__(self, src_dir, struc_gen):
        '''struc_gen should resemble:
                lambda p: struc(p, *<other_args>)
            where struc should resemble the ones defined in structure.py
            note that p doesn't have to be the first parameter in struc.__init__'''
        super(StrucScanFromTemplate, self).__init__(src_dir)
        self.struc_gen = struc_gen

    def _make_exp_name(self, header, p):
        return '{}_alat={:0.3e}'.format(header, p)

    def _alter_vaspin(self, exp_dir, exp_name, p):
        ToolKit.write_poscar_abs(
            struc=self.struc_gen(p), 
            outpath=os.path.join(exp_dir, 'POSCAR'))



class EcutScanFromTemplate(ScanFromTemplate):

    def __init__(self, src_dir):
        super(EcutScanFromTemplate, self).__init__(src_dir)

    def _make_exp_name(self, header, p):
        return '{}_ecut={}'.format(header, p)

    def _alter_vaspin(self, exp_dir, exp_name, p):
        ToolKit.alter_file(
            vasp.VaspINCAR, 
            os.path.join(exp_dir, 'INCAR'), 
            configs={'ENCUT': str(p)})



class KpointsScanFromTemplate(ScanFromTemplate):

    def __init__(self, src_dir):
        super(KpointsScanFromTemplate, self).__init__(src_dir)

    def _make_exp_name(self, header, p):
        return '{}_kgrid=[{}_{}_{}]'.format(header, *p)

    def _alter_vaspin(self, exp_dir, exp_name, p):
        ToolKit.alter_file(
            vasp.VaspKPOINTS, 
            os.path.join(exp_dir, 'KPOINTS'), 
            configs={'grid': p})



class SaxisScanFromTemplate(ScanFromTemplate):

    def __init__(self, src_dir):
        super(SaxisScanFromTemplate, self).__init__(src_dir)

    def _make_exp_name(self, header, p):
        return '{}_saxis=[{}_{}_{}]'.format(header, *p)

    def _alter_vaspin(self, exp_dir, exp_name, p):
        ToolKit.alter_file(
            vasp.VaspINCAR, 
            os.path.join(exp_dir, 'INCAR'), 
            configs={'SAXIS': '{} {} {}'.format(*p)})





#################### Develop from Old ####################

class NewScanFromOld(ScanFromTemplate):
    '''perform new scan based on old experiment results'''

    def __init__(self, new_dir, src_dir):
        '''src_dir contains the old experiment results
            new_dir contains the new scanner template'''
        super(NewScanFromOld, self).__init__(src_dir)
        assert(os.path.isdir(new_dir))
        self.new_dir = new_dir

    def make(self, param_list, out_dir, 
             incar_keeps=[], batch_keeps=[], 
             header=None, info=None, 
             overwrite=False, merge=False):
        '''much the same as in ScanFromTemplate,
            deploys ToolKit.continue_general to update POSCAR
            deploys ToolKit.switch_template to reconfigure batch file and INCAR
                incar_keeps, batch_keeps:   the input for ToolKit.switch_template()'''
        ToolKit.make_out_dir(out_dir, overwrite, merge)
        ToolKit.write_info(out_dir, info)
        for p in param_list:
            exp_name, exp_dir = self._init_exp(out_dir, header, p)
            if 'CONTCAR' in os.listdir(exp_dir):
                ToolKit.continue_general(exp_dir)
            self._switch_templates(exp_dir, incar_keeps, batch_keeps)
            self._alter_vaspin(exp_dir, exp_name, p)
            self._alter_batch(exp_dir, exp_name, p)

    def _make_exp_name(self, header, p):
        raise NotImplementedError

    def _alter_vaspin(self, exp_dir, exp_name, p):
        raise NotImplementedError

    def _switch_templates(self, exp_dir, incar_keeps, batch_keeps):
        ToolKit.switch_template(
            vasp.VaspINCAR, 
            os.path.join(exp_dir, 'INCAR'),
            os.path.join(self.new_dir, 'INCAR'),
            incar_keeps)
        ToolKit.switch_template(
            slurm.SlurmBatchScript,
            os.path.join(exp_dir, self.BATCHFILE),
            os.path.join(self.new_dir, self.BATCHFILE),
            batch_keeps)


class SaxisScanFromSTD(NewScanFromOld):

    def __init__(self, new_dir, src_dir):
        super(SaxisScanFromSTD, self).__init__(new_dir, src_dir)

    def _make_exp_name(self, header, p):
        return '{}_saxis=[{}_{}_{}]'.format(header, *p)

    def _alter_vaspin(self, exp_dir, exp_name, p):
        ToolKit.alter_file(
            vasp.VaspINCAR, 
            os.path.join(exp_dir, 'INCAR'), 
            configs={'SAXIS': '{} {} {}'.format(*p)})
        