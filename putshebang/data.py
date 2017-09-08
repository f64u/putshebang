# -*- coding: utf-8 -*-

"""the class that manipulates data"""
import os


class Data(object):
    INTERPRETERS = {}
    FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "langs.json")

    @staticmethod
    def load():
        with open(Data.FILE_PATH, "r") as f:
            Data.INTERPRETERS = eval(f.read())
            return Data.INTERPRETERS

    @staticmethod
    def save():
        with open(Data.FILE_PATH, "w") as f:
            f.write(Data.INTERPRETERS)

    @staticmethod
    def add_interpreter(ext, interpreter):
        inters = Data.INTERPRETERS.get(ext, [])
        if interpreter not in inters:
            inters.append(interpreter)
        Data.INTERPRETERS[ext] = inters
