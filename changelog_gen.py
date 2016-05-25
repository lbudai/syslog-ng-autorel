import pygit2, requests, re 

# GitHub API stuff
API_ENDPOINT  = 'https://api.github.com'
AUTHORISATION_HEADERS = {'Authorization' : ''} # specify auth headers

REPO = '/home/ank/gsoc16/dummy_project' # Specify the repository name here
USER = 'black-perl'
PROJECT_REPO = 'dummy_project'
commit_list = [] # List of commits
commit_lookup = {} # A hash to lookup whether a commit is considered in the changelog or not
pull_requests_ids = []
repo = pygit2.Repository(REPO)

# changelog entries lists
enhancement_entries = []
bugfix_entries = []
merged_pulls_entries = []
fixed_issues_entries = []
simple_commits_entries = []
# a dictionary corresponding to changelog
changelog_map = {
    "enhancement" : enhancement_entries,
    "bugfix" : bugfix_entries,
    "merged_pull" : merged_pulls_entries,
    "simple_commit" : simple_commits_entries,
    "fixed_issue" : fixed_issues_entries
}

class Entry:
    '''
        A changelog entry can be of one of the following category:
        - enchancement
        - bugfix
        - fixed_issues
        - merged_pulls
        - simple_commits
    '''
    def __init__(self,category):
        self.link = ''
        self.text = ''
        self.author_email = ''
        self.author_name = ''
        if category in changelog_map.keys():
            changelog_map[category].append(self)
        else:
            raise Exception('Invalid cateory specified')

    def addText(self,text):
        self.text = text

    def addLink(self,link):
        self.link = link

    def addMeta(self,name,email):
        '''
            Add meta data incase it is an external 
        '''
        self.author_name = name
        self.author_email = email


def get_pull_details(user,repo_name,pull_id):
    '''
        Fetches the pull request details for a given pull request id. Two cases basically
        - Pull request contains commits that closes some issues
          (these issues may further be categorised as bugs,enhancements if they have label)
        - Pull request doesn't involve any issue
    '''
    request_url = '{0}/repos/{1}/{2}/pulls/{3}/commits'.format(API_ENDPOINT,user,repo_name,pull_id)
    return requests.get(request_url,headers=AUTHORISATION_HEADERS).json()

def get_issue_details(user,repo_name,issue_id):
    '''
        An issue can be one of the following:
        - Bug 
        - Enhancement
        - Others
    '''
    request_url = '{0}/repos/{1}/{2}/issues/{3}'.format(API_ENDPOINT,user,repo_name,issue_id)
    return requests.get(request_url,headers=AUTHORISATION_HEADERS).json()

# Cookup commit list
for commit in repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL | pygit2.GIT_SORT_REVERSE):
    commit_list.append(commit)
    commit_lookup[commit.hex] = list([len(commit_list)-1,False])

# Find merge points 
for commit in commit_list:
    # check if the commit is a merge point or not
    if commit.message.startswith('Merge'):
        pull_request_id = commit.message.split(' ')[3][1:]
        pull_requests_ids.append(pull_request_id)
        # we have used the merge commit point, check it
        commit_lookup[commit.hex][1] = True

# find associated commits to a PR
for pull_id in pull_requests_ids:
    pull_details = get_pull_details(USER,PROJECT_REPO,pull_id)
    # involved commits in the pull request
    involved_commits_ids = []
    for entry in pull_details:
        involved_commits_ids.append(entry['sha'])
    # Now these are external commits, check if they are fixing some issue or not
    involved_issues_ids = []
    for commit_id in involved_commits_ids:
        commit = commit_list[commit_lookup[commit_id][0]]
        # We have used this commit, check it in hash
        commit_lookup[commit_id][1] = True
        commit_message = commit.message
        issues_ids = re.findall(r"(?<=#)\d+(?=\b)",commit_message)
        # commit does not corresponds to an issue
        if len(issues_ids) == 0:
            # these pulls are just merged, they don't fix an issue
            e = Entry('merged_pull')
            e.addText(commit_message)
            # TODO, fix this
            e.addLink('https://github.com/black-perl/dummy_project/pull/{0}'.format(pull_id))
            committer_name = commit.author.name
            committer_email = commit.author.email
            e.addMeta(committer_name,committer_email)
        else:
            # Ideally a commit should fix a single issue, but !
            for issue_id in issues_ids:
                issue_details = get_issue_details(USER,PROJECT_REPO,issue_id)
                # the issue does not correspond to any label
                issue_labels = []
                for label in issue_details['labels']:
                    issue_labels.append(label['name'])
                # a pull request always correspond to a bug fix or enchancement
                if 'bug' in issue_labels:
                    e = Entry('bugfix')
                elif 'enhancement' in issue_labels:
                    e = Entry('enhancement')
                else:
                    # the pulls fixes issues but they don't correspond to any labels
                    e = Entry('fixed_issue')
                # Set text and link
                e.addText(issue_details['title'])
                e.addLink(issue_details['html_url'])
                #add author info
                committer_name = commit.author.name
                committer_email = commit.author.email
                e.addMeta(committer_name,committer_email)


# find simple commits 
for commit in commit_list:
    # if the commit is not checked, it can be a simple commit or it can be one that is closing an issue
    if not (commit_lookup[commit.hex])[1]:
        commit_message = commit.message
        commit_lookup[commit.hex][1] = True
        issues_ids = re.findall(r"(?<=#)\d+(?=\b)",commit_message)
        # It is a simple commit
        if len(issues_ids) == 0:
            e = Entry('simple_commit')
            e.addText(commit_message)
        else:
            # Ideally a commit should fix a single issue, but !
            for issue_id in issues_ids:
                issue_details = get_issue_details(USER,PROJECT_REPO,issue_id)
                # the issue does not correspond to any label
                issue_labels = []
                for label in issue_details['labels']:
                    issue_labels.append(label['name'])
                # a pull request always correspond to a bug fix or enchancement
                if 'bug' in issue_labels:
                    e = Entry('bugfix')
                elif 'enhancement' in issue_labels:
                    e = Entry('enhancement')
                else:
                    # the pulls fixes issues but they don't correspond to any labels
                    e = Entry('fixed_issue')
                # Set text and link
                e.addText(issue_details['title'])
                e.addLink(issue_details['html_url'])
                #add author info
                committer_name = commit.author.name
                committer_email = commit.author.email
                e.addMeta(committer_name,committer_email)

# print changelog
for key in changelog_map.keys():
    print "=> {0}".format(key.upper())
    print "\n"
    for entry in changelog_map[key]:
        print entry.text,entry.link,entry.author_name,entry.author_email
        print '\n'
    print '===================================================================='