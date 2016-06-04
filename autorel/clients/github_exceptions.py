## Github Exceptions


class GithubException(Exception):

    """
        Exception handling for the Github client
    """

    def __init__(self, status_code, data):
        self._status = status_code
        self._data = data
        super(GithubException,self).__init__(self)

    @property
    def status(self):
        return self._status

    @property
    def data(self):
        return self._data

    def __str__(self):
        # The error dict object always have a key called message
        # (https://developer.github.com/v3/#client-errors)
        return self.status + " : " + self.data.get("message")


class BadCredentialsException(GithubException):

    """
        Exception raised when bad login credentials are encountered
        by the API server.
        https://developer.github.com/v3/#failed-login-limit
    """


class LoginAttemptExceededException(GithubException):

    """
        Exception raised when client makes multiple failed login attempts
    """


class UserAgentException(GithubException):

    """
        When a bad/no User-Agent header is involved
        https://developer.github.com/v3/#user-agent-required
    """


class RateLimitExceededException(GithubException):

    """
        Github API replies with a 403 when API rate limit exceeded
        https://developer.github.com/v3/#rate-limiting
    """


class ObjectNotFoundException(GithubException):

    """
        Requested object not found on the server
    """


class BadRequestException(GithubException):

    """
        An invalid json object is encountered by the server
        https://developer.github.com/v3/#client-errors
    """


class TwoFactorAuthException(GithubException):

    """
        Exception raised in case 2-Factor authenication in enabled by user
        https://developer.github.com/v3/auth/#working-with-two-factor-authentication
    """


class UnprocessableEntityException(GithubException):

    """
        The JSON data encountered by the server does not have correct type/value of attributes
    """

    def __str__(self):
        return self.status + " : " + self.data.get("message") + " " + self.data.get("errors")
