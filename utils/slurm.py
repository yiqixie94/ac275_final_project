'''
Slurm File templates
Author: Yiqi Xie
Date:   May 9, 2018
'''


from utils import template

class SlurmBatchScript(template.KVPFile):

    @classmethod
    def is_config(cls, line):
        line = line.strip()
        return line.startswith('#SBATCH')
    @classmethod
    def parse_config(cls, line):
        line = line.strip().partition(' ')[2]
        arg, _, info = line.partition('#')
        sep = '=' if arg.startswith('--') else ' '
        key, _, val = arg.partition(sep)
        return key.strip(), val.strip(), info.strip()
    @classmethod
    def make_config(cls, key, val, info):
        sep = '=' if key.startswith('--') else ' '
        arg = sep.join([key, val])
        line = ' '.join(['#SBATCH', arg])
        if info != '':
            line = '\t# '.join([line, info])
        line = ''.join([line, '\n'])
        return line
    @classmethod
    def mute_line(cls, line):
        line = ''.join(['#', line])
        return line