"""
    @module : syslogng_release
    @class : SyslogNgRelease
    - SyslogNgRelease class governs the release process
      of syslog-ng
"""
import pygit2
import os
import datetime
from autorel.changelog_generator import ChangelogGenerator
from autorel.utis import Docker
from autorel.build_helpers import (get_debian_source_building_commands,
                                   get_source_tarball_building_commands,
                                   debian_source_transformer,
                                   source_tarball_transformer
                                   )
from .platform import GithubPlatform
from .settings import (PACKAGE,
                       PROJECT,
                       PROJECT_CLONE_URL,
                       PROJECT_CLONE_PATH,
                       COMMITTER_NAME,
                       COMMITTER_EMAIL,
                       VERSION_FILE,
                       SOURCE_TARBALL_DOCKERFILE,
                       DEBIAN_SOURCE_DOCKERFILE,
                       PULL_REQUEST_TITLE,
                       PULL_REQUEST_BODY,
                       TZ_OFFSET,
                       DEBIAN_CHANGELOG_FILE,
                       DEBIAN_CHANGELOG
                       )


class SyslogNgRelease(object):
    def __init__(self, target_branch, release_name, release_tag, version):
        self._successful = False
        self._target_branch = target_branch
        self._release_name = release_name
        self._release_tag = release_tag
        self._version = version

    def _setup(self):
        """
            Setup the platform client for committer information
        """
        self._platform_cli = GithubPlatform(PROJECT)
        self._platform_cli.set_committer(COMMITTER_NAME,COMMITTER_EMAIL)
        self._version_bump_msg = "autorel bumped the version to {0}".format(self._version)
        self._tag_msg = "{0} release".format(self._release_name)

    def _clone_repo(self):
        """
            Clones the remote repository
        """
        self._repo = pygit2.clone_repository(url=PROJECT_CLONE_URL,
                                             path=PROJECT_CLONE_PATH,
                                             checkout_branch=self._target_branch
                                             )

    def _generate_changelog(self):
        """
            Generates the changelog
        """
        current_tag = self._platform_cli.get_current_release()
        latest_commit_sha = self._platform_cli.get_tagged_commit(current_tag)
        changelog_gen = ChangelogGenerator(PROJECT_CLONE_PATH,
                                           latest_commit_sha
                                           )
        return changelog_gen.render()

    def _create_release_branch(self):
        """
            Create a release branch from the target branch
        """
        self._release_branch = "release_{0}".format(self._release_tag)
        self._platform_cli.create_new_branch(self._target_branch,
                                             self._release_branch
                                             )

    def _increase_version(self):
        """
            Increase the version number in the repo
        """
        with open(VERSION_FILE,"w") as f:
            f.write(self._version)
        self._version_bump_commit = self._platform_cli.create_commit(self._release_branch,
                                                                     VERSION_FILE,
                                                                     self._version_bump_msg
                                                                     )

    def _edit_debian_changelog(self):
        date = datetime.datetime.now().isoformat()
        date += TZ_OFFSET
        debian_changelog = DEBIAN_CHANGELOG.format(PACKAGE_NAME=PACKAGE,
                                                   PACKAGE_VERSION=self._version,
                                                   RELEASE_TAG=self._release_tag,
                                                   CURRDATE=date
                                                   )
        with open(DEBIAN_CHANGELOG_FILE,"w") as f:
            f.write(debian_changelog)
        self._platform_cli.create_commit(self._release_branch,
                                         DEBIAN_CHANGELOG_FILE,
                                         self._version_bump_msg
                                         )


    def _create_tag(self):
        """
            Tag the last commit using the tag_name
        """
        self._platform_cli.create_annoted_tag(self._release_tag,
                                              self._tag_msg,
                                              self._version_bump_commit,
                                              "commit"
                                              )

    def _build_distball(self,source_locaction):
        """
            Generates the distribution tarball from the source code
        """
        build_commands = get_source_tarball_building_commands(source_locaction)
        docker = Docker()
        source_parent_directory = os.path.abspath(os.path.dirname(source_locaction))
        return docker.run(SOURCE_TARBALL_DOCKERFILE,
                          source_parent_directory,
                          build_commands,
                          source_tarball_transformer
                          )

    def _build_debian_source(self,distball_location):
        """
            Generated the debian source package
        """
        build_commands = get_debian_source_building_commands(distball_location)
        docker = Docker()
        distball_parent_directory = os.path.abspath(os.path.dirname(distball_location))
        return docker.run(DEBIAN_SOURCE_DOCKERFILE,
                          distball_parent_directory,
                          build_commands,
                          debian_source_transformer
                          )


    def _upload_to_obs(self):
        """
            Uploads the repository to OBS
        """
        pass
        # need to integrate with OBS


    def _send_pull_request(self):
        """
            Sends the pull request to the master branch
        """
        self._platform_cli.create_pull_request(self._version_bump_msg,
                                               PULL_REQUEST_TITLE,
                                               PULL_REQUEST_BODY,
                                               self._release_branch
                                               )

    
    def _send_mail(self):
        """
            Sends a mail to the mailing list regarding the new release
        """
        pass

    def _create_release_draft(self):
        # Need a way to upload the release asset
        # Need to look into the pygithub module
        pass

    def release(self):
        """
            Carry out the release operation
        """
        self._setup()
        self._clone_repo()
        changelog = self._generate_changelog()
        self._create_release_branch()
        self._increase_version()
        self._create_release_branch()
        self._create_tag()
        distball_location = self._build_distball(PROJECT_CLONE_PATH)
        debian_source_package = self._build_debian_source(distball_location)
        self._send_pull_request()