from clients.github_client import GithubInterface
from clients.helpers import Attribute, GithubDataType
from clients.commits import Commit


class PullRequest(GithubDataType):

    """
        Wrapper class across a Github pull request
    """
    def __init__(self, **kwargs):
        self.state = Attribute("The pull request state")
        self.base = Attribute("The base repo")
        self.head = Attribute("The head of the pull request")
        self.user = Attribute("The user who created the pull request")
        self.title = Attribute("The text of the pull request title")
        self.body = Attribute("The text of the body")
        self.number = Attribute("Number of this request")
        self.comments = Attribute("Number of comments made on this request")
        self.diff_url = Attribute("The URL to the unified diff")
        self.patch_url = Attribute("The URL to the downloadable patch")
        self.html_url = Attribute("The URL to the pull request")
        self.created_at = Attribute("The date when this pull request was created")
        self.updated_at = Attribute("The date when this pull request was last updated")
        self.closed_at = Attribute("The date when this pull request was closed")
        self.mergeable = Attribute("Whether the pull request can be merge cleanly")
        self.commits = Attribute("The number of commits packed up in the pull request")
        self.attributes = (
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
        super(PullRequest,self).__init__(**kwargs)


class PullRequests(GithubInterface):

    """
        Interface to Github Pull requests API
        GET /repos/:owner/:repo/pulls
        https://developer.github.com/v3/pulls
    """

    def __init__(self, client):
        self._requestor = client
        super(PullRequests,self).__init__(client)
        # Helper attributes to cook-up the request path
        self._path = None
        self._pathVars = None

    def pullDetails(self, project, pullID, **kwargs):
        """
            Get a single pull request
            https://developer.github.com/v3/pulls/#get-a-single-pull-request
        """
        self._path = "/repos/{owner}/{repo}/pulls/{pull_id}"
        self._pathVars = ["owner","repo","pull_id"]
        owner,repo = tuple(project.split("/"))
        return self.getValue(owner=owner,
                             repo=repo,
                             pull_id=pullID,
                             transform=PullRequest,
                             **kwargs
                             )

    def getCommits(self, project, pullID, **kwargs):
        """
            Get the commits involved in the pull request
            https://developer.github.com/v3/pulls/#list-commits-on-a-pull-request
        """
        self._path = "/repos/{owner}/{repo}/pulls/{pull_id}/commits"
        self._pathVars = ["owner","repo","pull_id"]
        owner,repo = tuple(project.split("/"))
        return self.getValues(owner=owner,
                              repo=repo,
                              pull_id=pullID,
                              transform=Commit,
                              **kwargs
                              )
