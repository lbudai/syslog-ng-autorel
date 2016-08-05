"""
	@module platform
	@class Platform
	- Abstracts out the platform dependence of the release cycle
	- All platfroms such as Github, Gitlab etc. comply with the API
"""
from github import Github
from .settings import GITHUB_AUTH_TOKEN



class Platform(object):
	def __init__(self, project):
		self._project = project
		self._client = Github(GITHUB_AUTH_TOKEN)
		self._repo = self._client.get_repo(self._project)

	def get_current_release():
		"""
			Get the latest release tag
		"""
		releases = []
		for release in self._repo.get_releases():
			releases.append(release)
		current_release = releases[0]
		return current_release.tag_name

	def create_new_branch(orig_branch, new_branch):
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

	
