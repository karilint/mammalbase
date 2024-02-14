""" Helper function to create, chdir and remove temp-dir where gathering and
zipping export files happens """
from os import getcwd, chdir
from shutil import rmtree
from tempfile import mkdtemp

def enter_temp_dir():
    """ Create and chdir to temporary directory """
    main_directory = getcwd()
    temp_directory = mkdtemp()
    chdir(temp_directory)
    return main_directory, temp_directory

def exit_temp_dir(main_directory, temp_directory):
    """ Changes directory and deletes temporaty directory tree """
    chdir(main_directory)
    rmtree(temp_directory)
