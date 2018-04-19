import os, sys, shutil
from utils import vasp, slurm, structure


BATCHFILE = 'batch.sh'
VASPINPUTS = ['INCAR', 'KPOINTS', 'POTCAR', 'POSCAR']


# class ParamScan:

#     @classmethod
#     def prepare_scan(cls, )
#     @classmethod
#     def prepare_trial(cls, pval, srcdir, trialdir, *args, **kwargs):
#         raise NotImplementedError



def prepare_lattice_scan(alat_range, vac, srcdir, outdir):
    srcbatchpath = os.path.join(srcdir, BATCHFILE)
    batch_template = slurm.SlurmBatchScript.load(srcbatchpath)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for a in alat_range:
        expname = 'monolayer_CrI3_alat={:0.3e}'.format(a)
        expdir = os.path.join(outdir, expname)
        exppath = os.path.join(expdir, BATCHFILE)
        if not os.path.exists(expdir):
            os.mkdir(expdir)
        expbatch = batch_template.develop(configs={'--job-name':expname})
        with open(exppath, 'w') as file:
            file.writelines(expbatch)
        for fname in VASPINPUTS:
            srcpath = os.path.join(srcdir, fname)
            exppath = os.path.join(expdir, fname)
            shutil.copy2(srcpath, exppath)
        poscarpath = os.path.join(expdir, 'POSCAR')
        struc = structure.MonoLayerCrI3(a, vac=vac)
        struc.write_poscar(poscarpath)
    return outdir
