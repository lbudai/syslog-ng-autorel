# syslog-ng-autorel
https://github.com/balabit/syslog-ng/wiki/GSoC2016-Idea-&amp;-Project-list#project-automated-release-generation-for-syslog-ng

Playing with github client
--------------------------

```Python
>>> # Make some imports
>>> from clients.github_client import Github
>>> from clients.pull_requests import PullRequests
>>> from clients.commits import Commits

>>> # Config for github client
>>> endpoint = "https://api.github.com"
>>> port = "443"
>>> user_agent = "syslong-ng/autorel"
>>> login = 'dummy'
>>> password = 'dummy_password'

>>> # Create a client instance
>>> cli = Github(endpoint,port,login,password,None,None,user_agent,None)

>>> # Create a pull request client
>>> pull = PullRequests(cli)

>>> # Fetch a specific pull request
>>> p = pull.pullDetails('balabit/syslog-ng', '1059', state='closed')
>>> p.title.value
'F/dbparser pdbload refact'
>>> p.commits.value
4

>>> # Fetch commits on a pull request
>>> c = pull.getCommits('balabit/syslog-ng', '1059')
>>> c
[<clients.commits.Commit object at 0x7fdb18b05668>, <clients.commits.Commit object at 0x7fdb17040c18>, 
<clients.commits.Commit object at 0x7fdb17a80eb8>, <clients.commits.Commit object at 0x7fdb1704cf98>]
>>> c[0].sha.value
'9058e8111993231d9220da354ad5fa5b675b7a1e'
```