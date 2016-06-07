from clients.github_client import GithubInterface
from clients.helpers import Attribute, GithubDataType


class Commit(GithubDataType):

    """
        Wrapper class across a Github commit
    """
    def __init__(self, **kwargs):
        self.sha = Attribute("Hash ID of the commit")
        self.url = Attribute("Commit URL")
        self.html_url = Attribute("URL of the page containing the commit information")
        self.comments_url = Attribute("Comments under the particular commit")
        # Author and Committer are different guys
        self.author = Attribute("Commit author details")
        self.committer = Attribute("Commit committer details")
        self.commit = Attribute("Metadata information about the commit")
        self.parents = Attribute("Parents of the commit")
        self.files = Attribute("Files undergoing changes during the commit")
        self.stats = Attribute("Some stats i.e Additions/Deletions etc.")
        self.attributes = (
            "sha",
            "url",
            "html_url",
            "comments_url",
            "author",
            "committer",
            "commit",
            "parents",
            "files",
            "stats"
        )
        super(Commit,self).__init__(**kwargs)


class Commits(GithubInterface):

    """
        Interface to Github Commits API
        GET /repos/:owner/:repo/commits
        https://developer.github.com/v3/repos/commits/
    """

    def __init__(self, client):
        self._requestor = client
        super(Commits,self).__init__(client)
        # Helper attributes to cook-up the request path
        self._path = None
        self._pathVars = None

    def getCommit(self, project, sha):
        """
            Retrieve a commit provided it's SHA
        """
        self._path = "repos/{owner}/{repo}/commits/{sha}"
        self._pathVars = ["owner","repo","sha"]
        owner,repo = tuple(project.split("/"))
        return self.getValue(owner=owner,
                             repo=repo,
                             sha=sha,
                             transform=Commit
                             )


