## Helper functions to fetch Pull Requests & Issues information from github
## To support GitLab and other platforms, similar helper functions should be wrote
from github import Github
from settings import (AUTH_TOKEN,
                      PROJECT
                      )
from structures import (PullRequest,
                        Issue,
                        Contributor,
                        Commit
                        )


# Instantiate the client
cli = Github(AUTH_TOKEN)


def getPull(pull_id):
    """
        Get details of a pull request.
        Should return a PullRequest instance
    """
    pull_id = int(pull_id)
    repo_obj = cli.get_repo(PROJECT)
    pull_req_obj = repo_obj.get_pull(pull_id)
    body = pull_req_obj.body
    url = pull_req_obj.html_url
    title = pull_req_obj.title
    contributor_name = pull_req_obj.user.name
    contributor_email = pull_req_obj.user.email
    contributor_url = pull_req_obj.user.url
    contributor = Contributor(contributor_name,
                              contributor_email,
                              contributor_url
                              )
    return PullRequest(title,
                       body,
                       contributor,
                       url
                       )


def getIssue(issue_id, pull_id=None, commit=None):
    """
        Get details of an issue
        -  An issue can be associated with an optional
           pull request
        -  A commit object carrying contributor infromation
    """
    issue_id = int(issue_id)
    if pull_id:
        pull_id = int(pull_id)
        pull_obj = getPull(pull_id)
    repo_obj = cli.get_repo(PROJECT)
    issue_obj = repo_obj.get_issue(issue_id)
    body = issue_obj.body
    url = issue_obj.html_url
    title = issue_obj.title
    labels_list = issue_obj.labels
    labels = []
    for label_obj in labels_list:
        labels.append(label_obj.name)
    if pull_obj:
        contributor = pull_obj.contributor
    elif commit:
        contributor = Contributor(commit.author.name,
                                  commit.author.email,
                                  None
                                  )
    else:
        pass
        #this won't be encountered

    return Issue(title,
                 body,
                 labels,
                 url,
                 pull_obj,
                 contributor
                 )




def getCommitList(pull_id):
    """
        Get linked commits to a pull request
    """
    pull_id = int(pull_id)
    repo_obj = cli.get_repo(PROJECT)
    pull_obj = repo_obj.get_pull(pull_id)
    paginated_commit_list = pull_obj.get_commits()
    commit_list = []
    for commit_obj in paginated_commit_list:
        commit_message = commit_obj.commit.message
        commit_sha = commit_obj.commit.sha
        c = Commit(commit_sha,
                   commit_message
                   )
        commit_list.append(c)
    return commit_list