"""
    module : dist_tarball
    This module is responsible for building syslog-ng from source
    in a docker environment and providing functionality of exporting
    the generated distribution tarball.
"""
import os
import glob


class DistTarballBuilder(object):
    """
        Responsible for downloading souce code and carry out
        build process to generate the distribution tarball.
    """
    def __init__(self, source_directory, image_name):
        self._source_directory = source_directory
        self._image_name = image_name

    @property
    def image(self):
        return self._image_name

    @property
    def source_directory(self):
        return self._source_directory

    @property
    def build_commands(self):
        """
            Returns the list of commands to be executed to
            build the distribution tarball
        """
        commands = [
            "(cd /home/syslog-ng && pip install -r requirements.txt)",
            "(cd /home/syslog-ng && ./autogen.sh)",
            "(cd /home/syslog-ng && mkdir build)",
            "(cd /home/syslog-ng/build && ../configure --enable-debug --prefix /opt/syslog-ng)",
            "(cd /home/syslog-ng/build && make -j)",
            "(cd /home/syslog-ng/build && make distcheck)"
        ]
        return commands

    @property
    def result(self):
        """
            Returns the path of the generated tarball on the
            host machine
        """
        lookup_directory = os.path.join(self._source_directory,
                                        "syslog-ng/build")
        os.chdir(lookup_directory)
        file_locations = glob.glob("syslog-ng-*.tar.gz")
        if len(file_locations) != 1:
            # TODO : Add appropriate class
            raise Exception("Tarball generation error")
        tarball_path = os.path.abspath(file_locations[0])
        return tarball_path

    def __str__(self):
        return "DistTarballBuilder : Distribution tarball builder class"