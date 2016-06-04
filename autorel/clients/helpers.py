## few Helper Classes


class NotSet(object):

    """
        A replacement for None
    """

    def __init__(self):
        pass


class Attribute(object):

    """
        Generic object attribute for definition of a
        GithubObject instance attribute
    """

    def __init__(self, help):
        self.help = help
        self._value = NotSet()

    @property
    def value(self):
        return self._value

    def setValue(self, value):
        self._value = value
