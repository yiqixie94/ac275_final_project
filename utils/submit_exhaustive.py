'''
Main script for a set of experiments
Submit the sublevel Slurm scripts all together
Upload this script to a Slurm system to run
Requires Python 2.7 (or higher)

Author: Yiqi Xie
Date:   May 9, 2018
'''


import os, sys, shutil
import time, io


class ChangeWD:
    ''' 
    changes working directory, 
    the designed syntax is like:
        with ChangeWD(workdir=newdir):
            do something
    after the "with" context, working directory recovers
    '''
    def __init__(self, workdir):
        self.wd = workdir
    def __enter__(self):
        self._orig_wd = os.getcwd()
        os.chdir(self.wd)
    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self._orig_wd)



def exhaust(root, depth=1, match=lambda fn:True):
    '''exhaust all files/folders that match a certain pattern within given depth
        default: depth=1, performs just like os.listdir(root)
        useful: depth=-1, performs somewhat like os.walk(root)
        note: for depth < 0 or depth as float, it exhausts all paths recursively under the root
    '''
    collect = []
    if depth != 0:
        for fname in os.listdir(root):
            fpath = os.path.join(root, fname)
            if match(fname):
                collect.append(fpath)
            if os.path.isdir(fpath):
                collect += exhaust(fpath, depth-1, match)
    return collect



def submit(fpath, logpath):
    '''executes 
        $ sbatch [script] > [logfile]'''
    fdir = os.path.dirname(fpath)
    with ChangeWD(workdir=fdir):
        os.system('sbatch {} > {}'.format(fpath, logpath))
    return



def main(root, depth=2, 
         match=lambda fn:fn.endswith('.sh'), 
         logpath=None, tmppath=None):
    if logpath is None:
        logpath = os.path.join(root, 'submit.log')
    if tmppath is None:
        tmppath = os.path.join(root, 'tmp.log')
    with open(logpath, 'w') as file: pass
    with open(tmppath, 'w') as file: pass
    fpathlist = exhaust(root, depth, match)
    for fpath in fpathlist:
        submit(fpath, tmppath)
        with open(tmppath, 'r') as ftmp:
            message = ftmp.readlines()[-1]
            sys.stdout.write(message)
        with open(logpath, 'a') as flog:
            flog.write(message.strip()+' \t'+fpath+'\n')
    os.remove(tmppath)
    return



if __name__ == '__main__':
    main(root=os.getcwd(), depth=2, match=lambda fn:fn.endswith('.sh'))


