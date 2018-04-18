import os, sys, shutil
import numpy as np
from utils import vasp, slurm
from utils import cri3


BATCHFILE = 'batch.sh'
VASPINPUTS = ['INCAR', 'KPOINTS', 'POTCAR', 'POSCAR']


def prepare_lattice_scan(alat_range, vac, srcdir, outdir):
    srcpath = os.path.join(srcdir, BATCHFILE)
    batch_template = slurm.SlurmBatchScript.load(srcpath)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for alat in alat_range:
        expname = 'monolayer_CrI3_alat_{:0.3e}'.format(alat)
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
        cri3.write_monolayer(alat, vac, poscarpath)
    return outdir