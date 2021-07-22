import os
import pathlib

from fastpy import constants

class Compiler:
    def __init__ (self, root_dir: pathlib.Path, main_file_name: str):
        self.root_dir = root_dir
        self.main_file_name = main_file_name
    def compile (self):
        assert os.system (f"clang++-10 -std=c++2a -o {self.root_dir}/{self.main_file_name} {self.root_dir}/src/{self.main_file_name}.cpp {constants.INCL_FLAG}") == 0
    def run (self):
        assert os.system (self.root_dir / self.main_file_name) == 0