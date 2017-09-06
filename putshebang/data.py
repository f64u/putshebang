
import os


class Data(object):
    SHEBANGS = None
    FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "langs.json")

    @staticmethod
    def load():
        with open(Data.FILE_PATH, "r") as f:
            Data.SHEBANGS = eval(f.read())
            return Data.SHEBANGS

    @staticmethod
    def save():
        with open(Data.FILE_PATH, "w") as f:
            f.write(Data.SHEBANGS)

    @staticmethod
    def add_shebang(ext, shebang):
        Data.SHEBANGS[ext] = shebang
