## A few Helper Classes


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


class GithubDataType(object):

    """
        Generic Wrapper class for wrapping Github Objects i.e
        Commits, Pull Requests
    """
    def __init__(self,**kwargs):
        """
            Set the attributes by using kwargs, the attributes meta
            information resides in `attributes` attribute
        """
        for attr in self.attributes:
            if attr in kwargs:
                attribute = getattr(self,attr)
                attribute.setValue(kwargs[attr])
            else:
                pass
                #raise KeyError("`{0}` not present in the response".format(attr))