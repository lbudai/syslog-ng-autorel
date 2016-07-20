"""
    module : debian_source_builder
    This module is responsible for building debian source package
    provided the distribution tarball directory
"""
import os
import glob


class DebianSourcePackage(object):
    """
        Result of running DebianSourceBuilder,
        represents a Debian source package
    """
    def __init__(self, distribution_tarball, patch_file, source_control_file):
        self._distribution_tarball = distribution_tarball
        self._patch_file = patch_file
        self._source_control_file = source_control_file

    @property
    def distribution_tarball_path(self):
        return self._distribution_tarball

    @property
    def patch_file_path(self):
        return self._patch_file

    @property
    def source_control_file_path(self):
        return self._source_control_file



class DebianSourceBuilder(object):
    """
        Responsible for creating debian source package from
        the distribution tarball.
    """
    def __init__(self, input_directory, image_name):
        self._input_directory = input_directory
        self._image_name = image_name

    @property
    def image(self):
        return self._image_name

    @property
    def input_directory(self):
        return self._input_directory

    @property
    def build_commands(self):
        """
            Returns the list of commands to be executed to
            build the debian source package
        """
        commands = [
            "(cd /home/ && tar -xvf syslog-ng_*)",
            "(cd /home/ && dpkg-source -Us -Uc -b syslog-ng-*"
        ]
        return commands

    @property
    def result(self):
        """
            Returns a DebianSourcePackage instance
        """
        lookup_directory = self._input_directory
        os.chdir(lookup_directory)
        distribution_tarball = glob.glob("*orig..tar.gz")[0]
        patch_file = glob.glob("*.tar.xz")[0]
        source_control_file = glob.glob("*.tar.dsc")[0]
        source_package = DebianSourcePackage(distribution_tarball,
                                             patch_file,
                                             source_control_file
                                             )
        return source_package

    def __str__(self):
        return "DebianSourceBuilder : DebianSourcePackage builder class"