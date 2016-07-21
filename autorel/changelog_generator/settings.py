"""
    @module settings
    Configuration options for changelog generator
"""
from changelog_generator.fetchers import GithubFetcher
from changelog_generator.parsers import (PullIDParser,
                                         MergedBranchParser,
                                         IssueIDParser
                                         )


FETCHER_PLUGIN = GithubFetcher
PULL_ID_PARSER = PullIDParser
MERGED_BRANCH_PARSER = MergedBranchParser
ISSUE_ID_PARSER = IssueIDParser

# Changelog Categories
ENHANCEMENT = "Enhancement"
BUGFIX = "BugFix"
FIXED_ISSUE = "Fixed Issue"
MERGED_PULL = "Merged Pull"
# Fetcher issue labels
BUG_LABEL = "bug"
ENHANCEMENT_LABEL = "enhancement"

FETCHER_AUTH_TOKEN = ""
PROJECT = "balabit/syslog-ng"
CLONE_URL = "git://github.com/balabit/syslog-ng.git"
