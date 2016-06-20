"""
    module : dist_tarball
    This module is responsible for building syslog-ng from source
    in a docker environment and providing functionality of exporting
    the generated distribution tarball.
"""
import logging
import tempfile
import pygit2
import os
import sys
import glob
from docker_cli import Docker



class DistTarballBuilder(object):
    """
        Responsible for downloading souce code and carry out
        build process to generate the distribution tarball.
    """
    def __init__(self, project, source_url, image_name):
        self._project = project
        self._source_url = source_url
        self._image_name = image_name
        self._docker_cli = Docker()
        # configure logger
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        channel = logging.StreamHandler(sys.stdout)
        channel.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        channel.setFormatter(formatter)
        self._logger.addHandler(channel)


    def _download_source(self):
        """
            Downloads the source code at a temporary directory
            on the host system
        """
        self._source_directory = tempfile.mkdtemp()
        repo_path = os.path.join(self._source_directory,
                                 'syslog-ng')
        pygit2.clone_repository(self._source_url,
                                path=repo_path)

    def setup(self):
        """
            Sets up the building environment by pulling the
            image using image_name and copies the downloaded
            source into the container
        """
        ## Download the source code
        self._logger.info("Downloading source code")
        self._download_source()
        self._logger.info("Souce code successfuly downloaded at {0}"
            .format(self._source_directory))

        ## Pull docker image
        self._logger.info("Pulling the {0} docker image"
            .format(self._image_name))
        self._docker_cli.cli_command("pull",
                                     repository=self._image_name)
        self._logger.info("Image successfuly pulled")

        ## Create a container in daemon mode
        self._logger.info("Running a container using the image")
        host_config = self._docker_cli.cli_command("create_host_config",
                                                   response=True,
                                                   binds={
                                                       self._source_directory : {
                                                           'bind': '/home/',
                                                           'mode': 'rw'
                                                       }
                                                   }
                                                   )
        container = self._docker_cli.cli_command("create_container",
                                                 response=True,
                                                 image=self._image_name,
                                                 detach=True,
                                                 command="tail -f /dev/null",
                                                 volumes=["/home/"],
                                                 host_config =host_config
                                                 )
        self._container_id = container.get("Id")
        # Start the container
        self._docker_cli.cli_command("start",
                                     response=True,
                                     container=self._container_id)
        self._logger.info("Container ({0}) is successfuly running"
            .format(self._container_id))


    def configure(self):
        """
            ./autogen.sh && configure
        """
        commands = [
            "(cd /home/syslog-ng && pip install -r requirements.txt) ; echo $?",
            "(cd /home/syslog-ng && ./autogen.sh) ; echo $?",
            "(cd /home/syslog-ng && mkdir build) ; echo $?",
            "(cd /home/syslog-ng/build && ../configure --enable-debug --prefix /opt/syslog-ng) ; echo $?"
        ]
        self._logger.info("Configuring: ./autogen.sh and ./configure")
        for cmd in commands:
            self._docker_cli.exec_in_container(self._container_id,
                                               cmd
                                               )
        self._logger.info("Configuration successful")


    def compile(self):
        """
            make -j
        """
        self._logger.info("Compiling : make -j")
        command = "(cd /home/syslog-ng/build && make -j ) ; echo $?"
        self._docker_cli.exec_in_container(self._container_id,
                                           command)
        self._logger.info("Compilation success")

    def distcheck(self):
        """
            make distcheck
        """
        self._logger.info("Running tests and creating tarball : make distcheck")
        command = "(cd /home/syslog-ng/build && make distcheck ) ; echo $?"
        self._docker_cli.exec_in_container(self._container_id,
                                           command)
        self._logger.info("All tests passed, distball generation complete")

    def getDistTarball(self):
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
        file_path = os.path.abspath(file_locations[0])
        return file_path


if __name__ == "__main__":
    d = DistTarballBuilder("balabit/syslog-ng",
                           "git://github.com/balabit/syslog-ng",
                           "ankcodes/syslog-ng-build")
    d.setup()
    d.configure()
    d.compile()
    d.distcheck()
    file_path = d.getDistTarball()
    print(file_path)
