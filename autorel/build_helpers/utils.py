"""
    @module utils
    Helper functions and classes used for building
    source tarballs and debian source packages
"""
import os
from builders.settings import (DEBIAN_SOURCE_BUILDING_IMAGE,
                               ORIG_TARBALL_FILE_WILDCARD,
                               PATCH_FILE_WIDLCARD,
                               SOURCE_CONTROL_FILE_WILDCARD,
                               SOURCE_DIRECTORY_WILDCARD,
                               SOURCE_TARBALL_BUILDING_IMAGE,
                               TARBALL_FILE_WILDCARD
                               )


    
class DebianSourcePackage(object):
    """
        Debian source package abstraction
    """
    def __init__(self, linked_tarball, patch_file, source_control_file):
        self._distribution_tarball = linked_tarball
        self._patch_file = patch_file
        self._source_control_file = source_control_file

    @property
    def linked_tarball_path(self):
        return self._linked_tarball

    @property
    def patch_file_path(self):
        return self._patch_file

    @property
    def source_control_file_path(self):
        return self._source_control_file


def get_debian_source_building_commands(source_location):
    """
        Returns the list of commands to be executed to
        build the debian source package
    """
    commands = [
        "(cd {0} && tar -xvf {1})".format(source_location,
                                          TARBALL_FILE_WILDCARD
                                          ),
        "(cd {0} && dpkg-source -Us -Uc -b {1}".format(source_location,
                                                       SOURCE_DIRECTORY_WILDCARD
                                                       )
    ]
    return commands


def get_source_tarball_building_commands(source_location):
    """
        Returns the list of commands to be executed to
        build the distribution tarball
    """
    commands = [
            "(cd {0} && pip install -r requirements.txt)",
            "(cd {0} && ./autogen.sh)",
            "(cd {0} && mkdir build)",
            "(cd {0}/build && ../configure --enable-debug)",
            "(cd {0}/build && make distcheck)"
    ]
    for command in commands:
        command.format(source_location)
    return commands

    
def debian_source_transformer(input_directory):
    """
        Returns a DebianSourcePackage instance
    """
    lookup_directory = input_directory
    os.chdir(lookup_directory)
    linked_tarball = glob.glob(ORIG_TARBALL_LOCATION)[0]
    patch_file = glob.glob(PATCH_FILE_WIDLCARD)[0]
    source_control_file = glob.glob(SOURCE_CONTROL_FILE_WILDCARD)[0]
    source_package = DebianSourcePackage(linked_tarball,
                                         patch_file,
                                         source_control_file
                                         )
    return source_package

    
def source_tarball_transformer(input_directory):
    """
        Returns the path of source tarball by looking into
        the input_directory
    """
    lookup_directory = input_directory 
    os.chdir(lookup_directory)
    distribution_tarball = glob.glob(TARBALL_FILE_WILDCARD)[0]
    distribution_tarball_path = os.path.abspath(distribution_tarball)
    return distribution_tarball_path
