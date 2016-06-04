from github_client import GithubObject
from helpers import Attribute


class PullRequest(GithubObject):

    """
        An interface to a Github Pull Request
    """
    state = Attribute("The pull request state")
    base = Attribute("The base repo")
    head = Attribute("The head of the pull request")
    user = Attribute("The user who created the pull request.")
    title = Attribute("The text of the pull request title.")
    body = Attribute("The text of the body.")
    number = Attribute("Number of this request.")
    comments = Attribute("Number of comments made on this request.")
    diff_url = Attribute("The URL to the unified diff.")
    patch_url = Attribute("The URL to the downloadable patch.")
    html_url = Attribute("The URL to the pull request.")
    created_at = Attribute("The date when this pull request was created.")
    updated_at = Attribute("The date when this pull request was last updated.")
    closed_at = Attribute("The date when this pull request was closed")
    mergeable = Attribute("Whether the pull request can be merge cleanly")
    commits = Attribute('The number of commits packed up in the pull request')

    _attributes = (
        "state",
        "base",
        "head",
        "user",
        "title",
        "body",
        "number",
        "comments",
        "diff_url",
        "patch_url",
        "html_url",
        "created_at",
        "updated_at",
        "closed_at",
        "mergeable",
        "commits"
    )

    def __init__(self, client, project, pullID):
        self._requestor = client
        self._path = "/repos/{owner}/{repo}/pulls/{pull_id}"
        self._pathVars = ["owner", "repo", "pull_id"]
        self._setAttributes(project, pullID)

    def _setAttributes(self, project, pullID):
        """
            Project str <owner>/<project>
            pullID  int
        """
        owner, repo = tuple(project.split('/'))
        self._request(owner=owner,
                      repo=repo,
                      pull_id=pullID
                      )
        # Set the value of each of the attribute
        for attribute_name in self._attributes:
            attribute = getattr(self, attribute_name)
            # Transform is None for now
            attribute_value = self.getValue(attribute_name, None)
            attribute.setValue(attribute_value)
