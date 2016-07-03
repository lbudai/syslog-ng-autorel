"""
    Module : docker_cli
    This module provides abstraction layer over docker-py
"""
import logging
import sys
from docker import Client


class ExecutionFailure(Exception):
    """
        Exception thrown when a command fails
        to execute successfuly
    """
    def __init__(self, message):
        super(self, FailedCommand).__init__(self)
        self._message = message

    def __str__(self):
        return self._message


class Docker(object):
    """
        Build the source code in a docker environment using the
        supplied builder instance
    """
    def __init__(self):
        self._cli = Client(base_url="unix://var/run/docker.sock",
                           version="auto"
                           )
        # container running flag
        self._running = False
        # configure logger
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        channel = logging.StreamHandler(sys.stdout)
        channel.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        channel.setFormatter(formatter)
        self._logger.addHandler(channel)

    def _cli_command(self, command_, *args, response=False, **kwargs):
        """
            Runs a docker client command and returns output if response
            flag is set to be True
        """
        self._logger.debug("Running {0} command on docker client"
            .format(command_))
        command = getattr(self._cli, command_)
        if response:
            result = command(*args, **kwargs)
            if isinstance(result, bytes):
                result = result.decode('utf-8')
            self._logger.debug(result)
            return result
        else:
            # set the output of client command to be a generator
            kwargs['stream'] = True
            for line in command(*args, **kwargs):
                line = line.decode('utf-8')
                self._logger.debug(line)

    def _exec_in_container(self, command_):
        """
            Executes a command in a running docker container
            and checks for the execution status
        """
        cmd = 'bash -c \"{0}\"'.format(command_)
        self._logger.debug("Executing in container ({0}) : {1}"
            .format(self._container_id,cmd))
        exec_instance = self._cli_command("exec_create",
                                          response=True,
                                          container=self._container_id,
                                          cmd=cmd
                                          )
        exec_id = exec_instance.get('Id')
        self._cli_command("exec_start",
                          exec_id
                          )
        exec_status = self._cli_command("exec_inspect",
                                        exec_id,
                                        response=True
                                        )
        if exec_status["ExitCode"] != 0:
            raise ExecutionFailure(response)


    def _setup(self, image, source_directory):
        """
            Sets up the building environment by pulling the
            image and starting the docker container
        """
        ## Pull the docker image
        self._logger.info("Pulling the {0} docker image"
            .format(image))
        self._cli_command("pull",
                          repository=image
                          )
        self._logger.info("Image successfuly pulled")

        ## Create a container in daemon mode
        self._logger.info("Running a container using the image")
        host_config = self._cli_command("create_host_config",
                                        response=True,
                                        binds={
                                            source_directory : {
                                                   'bind': '/home/',
                                                   'mode': 'rw'
                                               }
                                            }
                                        )
        container = self._cli_command("create_container",
                                      response=True,
                                      image=image,
                                      detach=True,
                                      command="tail -f /dev/null",
                                      volumes=["/home/"],
                                      host_config =host_config
                                      )
        self._container_id = container.get("Id")
        # Start the container
        self._cli_command("start",
                          response=True,
                          container=self._container_id)
        self._running = True
        self._logger.info("Container ({0}) is successfuly running"
            .format(self._container_id))

    def run(self, builder):
        """
            Runs build instructions corresponding to
            a builder instance
        """
        if self._running:
            raise Exception("Another container is running with ID : {0}"
                .format(self._container_id))
        self._setup(builder.image,
                    builder.source_directory)
        self._logger.info("Running {0}".format(builder))
        for cmd in builder.build_commands:
            self._logger.info("Running : {0}".format(cmd))
            self._exec_in_container(cmd)
            self._logger.info("Finished : {0}".format(cmd))
        self._logger.info("Finished {0}".format(builder))
        # Stop the container
        self._cli_command("stop",
                          container=self._container_id)
        self._running = False
        return builder.result