# -*- coding: utf-8 -*-

"""the class that manipulates data"""
import json
import os
from pprint import pprint

from . import Interpreter, InterpreterPath


class Data(object):
    INTERPRETERS = {}
    FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "langs.json")

    @staticmethod
    def load():
        with open(Data.FILE_PATH, "r") as f:
            data = json.load(f)
            pprint(data)
            return Data.INTERPRETERS

    @staticmethod
    def save():
        with open(Data.FILE_PATH, "w") as f:
            json.dump(Data.INTERPRETERS, f)

    @staticmethod
    def add_interpreter(ext, interpreter):
        inters = Data.INTERPRETERS.get(ext, [])
        if interpreter not in inters:
            inters.append(interpreter)
        Data.INTERPRETERS[ext] = inters

if __name__ == '__main__':
    Data.load()
