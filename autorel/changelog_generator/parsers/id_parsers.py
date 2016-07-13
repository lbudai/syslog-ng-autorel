## Register your parsing functions here

import re


def pull_id_parser(msg_body):
    """
        Parses pull request id from commit message
        => msg : Merge pull request #1234 from username/branch
        => pull_id : 1234
    """
    if msg_body.startswith('Merge pull'):
        tokens = msg_body.split()
        pull_id = tokens[3][1:]
        return pull_id, "pull_id"


def pull_branch_parser(msg_body):
    """
        Parses branch name from commit message
        => msg : Merge from user/master
        => branch_name : user/master
    """
    if msg_body.startswith('Merge branch'):
        tokens = msg_body.split()
        pull_branch = tokens[2]
        return pull_branch, "merged_branch"


def issue_id_parser(msg_body):
    """
        Parses the issue id from commit message
        => msg : Fixes #1234
        => issue_id : 1234
        It can also be used to parse pull request body for
        the linked issue.
    """
    result1 = re.findall(r"fix\s+#(\d+)(?=\b)",msg_body,re.IGNORECASE)
    result2 = re.findall(r"fixes\s+#(\d+)(?=\b)",msg_body,re.IGNORECASE)
    issue_ids = list(set(result1).union(set(result2)))
    if len(issue_ids):
        return issue_ids, "issue_ids"


PARSING_FUNCTIONS = {
    "merges": [
        pull_id_parser,
        pull_branch_parser
    ],
    "issues": [
        issue_id_parser
    ],
}

__all__ = [PARSING_FUNCTIONS]