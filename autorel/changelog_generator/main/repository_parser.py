## Helper classes for parsing pull requests ids, issues ids etc.

class Parser(object):
    """
        Helper class to parse message bodies for pull request
        and issues ids
    """
    def __init__(self, supportedTypes):
        self._supportedTypes = supportedTypes
        self._parsers = {}
        for type_ in self._supportedTypes:
            # a list of functions to parse type_ messages
            self._parsers[type_] = []

    def addParser(self, parserType, function):
        if parserType in self._supportedTypes:
            self._parsers[parserType].append(function)
        else:
            raise ValueError('{0} pattern type not supported'.format(parserType))

    def parse(self, patternType, msg_body):
        """
            Parses a message body using the available parsers
            Return value may be
            - a pull request id
            - an issue id
            - a branch name
        """
        for parsing_func in self._parsers[patternType]:
            parser_output = parsing_func(msg_body)
            if parser_output:
                parsed_value, type_ = parser_output
                return parser_output
