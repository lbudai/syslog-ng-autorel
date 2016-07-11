## Main changelog generation logic goes here
import pygit2
from parser import Parser
from parser_config import PARSING_FUNCTIONS
from structures import (PullRequest,
                        Issue,
                        Contributor
                        )
from settings import (PROJECT,
                      CLONE_URL
                      )
from github_plugin import (getPull,
                           getCommitList,
                           getIssue
                           )


class ChangelogEntry(object):
    """
        Defines a changelog entry
    """
    def __init__(self, category, contributor, url, text):
        self._category = category
        self._contributor = contributor
        self._url = url
        self._text = text

    @property
    def url(self):
        return self._url

    @property
    def text(self):
        return self._text

    @property
    def contributor(self):
        return self._contributor

    @property
    def category(self):
        return self._category


class ChangelogGenerator(object):
    """
        The Changelog Generator class
    """
    # The generated changelog will contain the following categories
    categories = (
        "enhancement",
        "bugfix",
        "fixed_issue",
        "merged_pull"
    )

    def __init__(self):
        self._user,self._repoName = tuple(PROJECT.split('/'))
        # A dict of ChangelogEntry objects
        self._entries = {}
        # Initialise the supported categories
        for entry in self.categories:
            self._entries[entry] = []
        # List of commit objects for the repo
        self._commits = []
        # A dict to keep track of traversal of commits
        self._commit_map = {}

    def _configure_parser(self):
        """
            Configure the parser for different paring funtions
        """
        self._parser = Parser(["issues","merges"])
        for type_ in PARSING_FUNCTIONS.keys():
            for parsing_func in PARSING_FUNCTIONS[type_]:
                self._parser.addParser(type_,parsing_func)

    def _clone_repository(self):
        """
            Clone and instanstiate a repo instance
        """
        clone_path = '/tmp/{0}'.format(self._repoName)
        self._repo = pygit2.Repository(clone_path)
        #self._repo = pygit2.clone_repository(CLONE_URL,clone_path)

    def _generate_commit_map(self):
        # TODO : change the head according to last tagged commit
        tag_commit = "af342a6c677e7c5da6b1cacebfc3019cbe870e43"
        for commit in self._repo.walk(self._repo.head.target,
                      pygit2.GIT_SORT_TOPOLOGICAL):
            # Stop at this
            if commit.hex  == tag_commit:
                break
            self._commits.append(commit)
            # key <= commit hex value & value <= (chronological order of commit,visited)
            # Initially all commit nodes are unvisited, so set it false
            self._commit_map[commit.hex] = list([len(self._commits)-1,False])

    def _add_changelog_entry(self, entry_obj):
        """
            Add an entry to the changelog
        """
        if isinstance(entry_obj,PullRequest):
            category = "merged_pull"
            changelog_entry = ChangelogEntry(category,
                                             entry_obj.contributor,
                                             entry_obj.url,
                                             entry_obj.title
                                             )
        elif isinstance(entry_obj,Issue):
            if "bug" in entry_obj.labels:
                category = "bugfix"
            elif "enhancement" in entry_obj.labels:
                category = "enhancement"
            else:
                category = "fixed_issue"
            changelog_entry = ChangelogEntry(category,
                                             entry_obj.contributor,
                                             entry_obj.url,
                                             entry_obj.title
                                             )
        elif isinstance(entry_obj,ChangelogEntry):
            changelog_entry = entry_obj
            category = entry_obj.category

        self._entries[category].append(changelog_entry)

    def _parse_commits_for_merge_nodes(self):
        """
            Parse the merge commit messages for the pull request identifiers
            or the branch names
        """
        merge_commits = []
        self._pull_ids = []

        for commit in self._commits:
            # A merge commit has at least 2 parent commits
            # in case its a standard pull request merge
            if len(commit.parents) >= 2:
                merge_commits.append(commit)
            # The case when we avoid the extra "merge commit"
            # Commit squashing case
            elif commit.author != commit.committer:
                merge_commits.append(commit)

        # parse the merge commits
        for commit in merge_commits:
            self._commit_map[commit.hex][1] = True # Mark the node visited
            parsed_data = self._parser.parse("merges", commit.message)
            if parsed_data:
                # CASE 1 : It is a local checkout
                if parsed_data[1] == "merged_branch":
                    branch_description = parsed_data[0]
                    # Create changelog entry for the merged branch
                    contributor = Contributor(commit.author.name,
                                              commit.author.email,
                                              None
                                              )
                    changelog_entry = ChangelogEntry("merged_pull",
                                                     contributor,
                                                     None,
                                                     "{0} : {1}".format(branch_description,
                                                                        commit.message.split('\n')[0])
                                                     )
                    self._add_changelog_entry(changelog_entry)
                # CASE 2 : It is a pull request
                elif parsed_data[1] == "pull_id":
                    pull_request_id = parsed_data[0]
                    self._pull_ids.append(pull_request_id)
            else:
                # Debugging
                #print(commit.message)
                pass

    def _mark_merged_commits(self):
        """
            Mark the merged commits visited
        """
        for pull_id in self._pull_ids:
            involved_commits = getCommitList(pull_id)
            for commit in involved_commits:
                # Mark the commit nodes visited
                try:
                    self._commit_map[commit.hex][1] = True
                except KeyError:
                    # When the commit is not part of this release
                    pass

    def _parse_commits_for_issue_nodes(self):
        """
            Parses the commits messages for the issue ids
        """
        issue_commit_list = []
        for commit in self._commits:
            # the commit node should be unvisited
            if self._commit_map[commit.hex][1] is False:
                parsed_data = self._parser.parse("issues", commit.message)
                if parsed_data:
                    if parsed_data[1] == "issue_ids":
                        issue_ids = parsed_data[0]
                        for issue_id in issue_ids:
                            issue_commit_list.append(tuple((
                                                        commit,
                                                        issue_id
                                                    )))
                    # mark the commit node visited
                    self._commit_map[commit.hex][1] = True
        # Create changelog entries for all the independent issues
        for element in issue_commit_list:
            issue_id = element[1]
            commit = element[0]
            issue_obj = getIssue(issue_id,
                                 commit=commit
                                 )
            self._add_changelog_entry(issue_obj)

    def _extract_linked_issues(self):
        """
            Extract issues linked to pull requests
        """
        issue_pull_list = []
        for pull_detail in self._pull_ids:
            pull_id = pull_detail
            pull_obj = getPull(pull_id)
            parsed_data = self._parser.parse("issues", pull_obj.body)
            if parsed_data:
                if parsed_data[1] == "issue_ids":
                    issue_ids = parsed_data[0]
                    for issue_id in issue_ids:
                        issue_pull_list.append(tuple((
                                                pull_id,
                                                issue_id
                                              )))
            else:
                self._add_changelog_entry(pull_obj)

        # Create changelog entries for all the issues liked with pull requests
        for element in issue_pull_list:
            issue_id = element[1]
            pull_id = element[0]
            issue_obj = getIssue(issue_id,
                                 pull_id=pull_id
                                 )
            self._add_changelog_entry(issue_obj)

    def generate(self):
        """
            Generate the changelog according to last provided tag
        """
        self._clone_repository()
        self._generate_commit_map()
        self._configure_parser()
        self._parse_commits_for_merge_nodes()
        self._mark_merged_commits()
        self._parse_commits_for_issue_nodes()
        self._extract_linked_issues()

    def render(self):
        """
            Render the changelog in markdown format
        """
        for key in self._entries:
            print(key)
            print("--------")
            print("--------")
            print("\n\n")
            for entry in self._entries[key]:
                print("- {0}     [Link]({1})    {3}".format(entry.text,
                                                    entry.url,
                                                    entry.committer.name
                                                    )
                     )
                print('\n')


if __name__ == "__main__":
    generator = ChangelogGenerator()
    generator.generate()
    generator.render()
