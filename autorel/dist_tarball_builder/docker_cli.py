"""
    Module : docker
    This module provides abstraction layer over docker-py
"""
import logging
import sys
from docker import Client


class Docker(object):
    """
        Abstraction over docker-py to provide logging functionality
        and status checking of command execution
    """
    def __init__(self):
        self._cli = Client(base_url="unix://var/run/docker.sock",
                           version="auto"
                           )
        # configure logger
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        channel = logging.StreamHandler(sys.stdout)
        channel.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        channel.setFormatter(formatter)
        self._logger.addHandler(channel)

    def cli_command(self, command_, *args, response=False, check_execution_status = False, **kwargs):
        """
            Runs a docker client command and returns output if response
            flag is set to be True else a streamed response is sent to the
            debug log section.
            Also, Checks the execution status of a command provided
            check_execution_status flag is set.
        """
        self._logger.debug("Running {0} command on docker client"
            .format(command_))
        command = getattr(self._cli, command_)
        if response:
            result = command(*args, **kwargs)
            if isinstance(result, bytes):
                result = result.decode('utf-8')
            self._logger.debug(result)
            # check execution status
            if check_execution_status:
                result_list = result.strip().split('\n')
                if result_list[-1] != '0':
                    # TODO : Create a class for this exception
                    raise Exception("command : {0} failed".format(command_))
            return result
        else:
            # set the output of client command to be a generator
            kwargs['stream'] = True
            for line in command(*args, **kwargs):
                line = line.decode('utf-8')
                self._logger.debug(line)
            # check execution status
            execution_status = line.strip()
            if check_execution_status and execution_status != '0':
                    # TODO : Create a class for this exception
                    raise Exception("command : {0} failed".format(command_))

    def exec_in_container(self, container_id, cmd):
        """
            Executes a command in a running docker container
            and checks for the execution status
        """
        cmd = 'bash -c \"{0}\"'.format(cmd)
        self._logger.debug("Executing in container ({0}) : {1}"
            .format(container_id,cmd))
        exec_instance = self.cli_command("exec_create",
                                         response=True,
                                         container=container_id,
                                         cmd=cmd
                                         )
        self.cli_command("exec_start",
                         exec_instance.get('Id'),
                         check_execution_status=True
                         )
