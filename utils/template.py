import os, sys


class ConfigTemplate:

    def __init__(self, tlines):
        self.tlines = tlines
        self.cfgdict = self.parse_template(tlines)

    def develop(self, configs=None, cmtouts=None):
        if configs is None:
            configs = {}
        if cmtouts is None:
            cmtouts = []
        configs_ = {str(k):str(v) for k,v in configs.items()}
        cmtouts_ = [str(k) for k in cmtouts]
        new_cfgdict = {}
        for key, (i, val, info) in self.cfgdict.items():
            if key in configs_:
                val = configs_[key]
            new_cfgdict[key] = (i, val, info)
        new_tlines = list(self.tlines)
        for key, (i, val, info) in new_cfgdict.items():
            if key in cmtouts_:
                new_tlines[i] = self.disable_line(new_tlines[i])
            else:
                new_tlines[i] = self.make_config(key, val, info)
        return new_tlines

    @classmethod
    def load(cls, fpath, mode='r'):
        with open(fpath, mode) as file:
            template = cls(file.readlines())
        return template

    @classmethod
    def parse_template(cls, tlines):
        result = {}
        for i, line in enumerate(tlines):
            if cls.is_config(line):
                key, val, info = cls.parse_config(line)
                result[key] = (i, val, info)
        return result

    @classmethod
    def is_config(cls, line):
        raise NotImplementedError
    
    @classmethod
    def parse_config(cls, line):
        raise NotImplementedError

    @classmethod
    def make_config(cls, key, val, info):
        raise NotImplementedError

    @classmethod
    def disable_line(cls, line):
        raise NotImplementedError