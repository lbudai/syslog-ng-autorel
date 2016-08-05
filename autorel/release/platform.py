"""
    @module platform
    @class Platform
    - Abstracts out the platform dependence of the release cycle
    - All platfroms such as Github, Gitlab etc. comply with the API
"""
import datetime
from github import (Github,
                    InputGitTreeElement,
                    InputGitAuthor
                    )
from .settings import GITHUB_AUTH_TOKEN


class Platform(object):
    """
        Exposes higher level platform API
    """
    def __init__(self, project):
        self._project = project
        self._client = Github(GITHUB_AUTH_TOKEN)
        self._repo = self._client.get_repo(self._project)

    def add_committer(self, name, email):
        """
            Create a git committer/author
        """
        date = datetime.datetime.utcnow().isoformat()
        self._committer = InputGitAuthor(name=name,
                                         email=email,
                                         date=date
                                         )

    def get_current_release(self):
        """
            Get the latest release tag
        """
        releases = []
        for release in self._repo.get_releases():
            releases.append(release)
        current_release = releases[0]
        return current_release.tag_name

    def create_new_branch(self, orig_branch, new_branch):
        """
            Creates a new branch from the orig_branch
        """
        if not orig_branch.startwith("heads/"):
            orig_branch = "heads/" + orig_branch
        if not new_branch.startwith("refs/heads/"):
            new_branch = "refs/heads/" + new_branch
        # Get the SHA value of the latest commit on the orig_branch
        orig_branch_ref = self._repo.get_git_ref(orig_branch)
        latest_commit_sha = orig_branch_ref.object.sha
        self._repo.create_git_ref(new_branch,latest_commit_sha)

    def create_commit(self, orig_branch, file_path, commit_message):
        """
            Creates a commit to the orig_branch by adding a file given by file_path
            and using a provided commit_message
        """
        ## find the latest commit SHA on the orig_branch
        orig_branch_ref = self._repo.get_git_ref(orig_branch)
        latest_commit_sha = orig_branch_ref.object.sha
        ## find the base tree to be written out
        latest_commit = self._repo.get_commit(latest_commit_sha)
        base_tree = latest_commit.commit.tree
        ## create a new tree
        with open(file_path,'r') as f:
            file_contents = f.read()
        # specifications required to create a new tree
        new_tree_specs = InputGitTreeElement(path=file_path,
                                             mode="100644",
                                             type="blob",
                                             content=file_contents
                                             )
        new_tree = self._repo.create_git_tree(base_tree=base_tree,
                                              tree=[new_tree_specs]
                                              )
        ## create a new commit on the new_tree
        parent_commits = [latest_commit]
        created_commit = self._repo.create_git_commit(message=commit_message,
                                                      tree=new_tree,
                                                      parents=parent_commits,
                                                      author=self._committer,
                                                      committer=self._committer
                                                      )
        ## update the orig_branch to reference created_commit
        orig_branch_ref.edit(sha=created_commit.sha)