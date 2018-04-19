class DataType:

    @classmethod
    def istype(cls, val):
        raise NotImplementedError
    @classmethod
    def decode(cls, val, *args, **kwargs):
        raise NotImplementedError
    @classmethod
    def encode(cls, pyval, *args, **kwargs):
        raise NotImplementedError
    @classmethod
    def decode_elewise(cls, vals, *args, **kwargs):
        return [cls.decode(v, *args, **kwargs) for v in vals]
    @classmethod
    def encode_elewise(cls, pyvals, *args, **kwargs):
        return [cls.encode(v, *args, **kwargs) for v in pyvals]
    @classmethod
    def unify(cls, string, sep, encoder_params={}, decoder_params={}):
        string_ = []
        for s in string.split(sep):
            if cls.istype(s):
                s = cls.decode(s, **decoder_params)
                s = cls.encode(s, **encoder_params)
            string_.append(s)
        string_ = sep.join(string_)
        return string_



class Parser:

    def __init__(self, flines):
        self.contents = self.parse(flines)
    @classmethod
    def load(cls, fpath):
        with open(fpath, 'r') as file:
            flines = file.readlines()
        return cls(flines)
    @classmethod
    def parse(cls, flines, *args, **kwargs):
        raise NotImplementedError



class CreatableFile(Parser):

    def __init__(self, flines):
        self.flines = flines
        self.contents = self.parse(flines)
    @classmethod
    def from_scratch(cls, *args, **kwargs):
        flines = cls.create(*args, **kwargs)
        return cls(flines)
    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError
    @classmethod
    def parse(cls, flines, *args, **kwargs):
        raise NotImplementedError



class AlterableFile(Parser):

    def __init__(self, flines):
        self.flines = flines
        self.contents = self.parse(flines)
    def alter(self, configs=None, mutes=None, **kwargs):
        raise NotImplementedError
    @classmethod
    def parse(cls, flines, *args, **kwargs):
        raise NotImplementedError



class FreeFile(CreatableFile, AlterableFile):

    def __init__(self, flines):
        self.flines = flines
        self.contents = self.parse(flines)
    def alter(self, configs={}, mutes=[], **kwargs):
        configs_ = dict(self.contents)
        for key, val in configs.items():
            if key in configs_:
                configs_[key] = val
        return self.create(**configs_)
    @classmethod
    def from_scratch(cls, *args, **kwargs):
        flines = cls.create(*args, **kwargs)
        return cls(flines)
    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError
    @classmethod
    def parse(cls, flines, *args, **kwargs):
        raise NotImplementedError



class KVPFile(AlterableFile):
    '''key-value-paired file'''

    def alter(self, configs={}, mutes=[], **kwargs):
        configs_ = {str(k):str(v) for k,v in configs.items()}
        mutes_ = [str(k) for k in mutes]
        newdict = {}
        for key, (i, val, info) in self.contents.items():
            if key in configs_:
                val = configs_[key]
            newdict[key] = (i, val, info)
        newlines = list(self.flines)
        for key, (i, val, info) in newdict.items():
            if key in mutes_:
                newlines[i] = self.mute_line(newlines[i])
            else:
                newlines[i] = self.make_config(key, val, info)
        return newlines
    @classmethod
    def parse(cls, flines, *args, **kwargs):
        result = {}
        for i, line in enumerate(flines):
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
    def mute_line(cls, line):
        raise NotImplementedError