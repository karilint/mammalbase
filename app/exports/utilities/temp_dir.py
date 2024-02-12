from os import getcwd, chdir
from shutil import rmtree
from tempfile import mkdtemp

def enter_temp_dir():
    current_dir = getcwd()
    temp_directory = mkdtemp()
    chdir(temp_directory)
    return current_dir, temp_directory

def exit_temp_dir(current_dir, temp_directory):
    chdir(current_dir)
    rmtree(temp_directory)
