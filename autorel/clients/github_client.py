import base64, re
from http_client import HTTPClient
from github_exceptions import *

class Github:
    '''
        Client interacting with the Github REST API
    '''
    def __init__(self,endpoint,port,token_or_login,password,clientID,clientSecret,userAgent,timeout):
        self._authorizationHeaders = {}
        self._params = {} # URL-parameters
        if password is not None:
            # https://developer.github.com/v3/#basic-authentication
            username = token_or_login()
            auth_string = username + ':' + password
            self._authorizationHeaders = "Basic " + base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        elif password is None:
            # https://developer.github.com/v3/#oauth2-token-sent-in-a-header
            self._authorizationHeaders = "token " + token_or_login
        elif clientID and clientSecret:
            # https://developer.github.com/v3/#oauth2-keysecret
            self._params["client_id"] = clientID
            self._params["client_secret"] = clientSecret
        # Github API requires a user agent, if provided else fallback to what HTTPClient is using
        if userAgent:
            self.headers['User-Agent'] = userAgent
        # Accept only version 3 of the API ( https://developer.github.com/v3/#current-version )
        self.headers['Accept'] = 'application/vnd.github.v3+json'
        self._client = HTTPClient(endpoint,port,self._headers,self._params,timeout)

    def _doExceptionHandling(self,status_code,headers,data):
        '''
            Check the response for possible exceptions
        '''
        exception_class = None
        if status_code == 401 and data.get("message") == 'Bad credentials':
            exception_class = BadCredentialsException
        elif status_code == 403 and data.get("message").startswith('Maximum number'):
            exception_class = LoginAttemptExceededException
        elif status_code == 403 and data.get("message").startswith("API Rate Limit Exceeded"):
            exception_class = RateLimitExceededException
        elif status_code == 403 and data.get("message").startswith("Missing or invalid User Agent string"):
            exception_class = UserAgentException
        elif status_code == 404 and data.get("message") == "Not Found":
            exception_class = ObjectNotFoundException
        elif status_code == 400:
            exception_class = BadRequestException
        elif status_code == 422:
            exception_class = UnprocessableEntityException
        elif status == 401 and 'X-GitHub-OTP' in headers and re.match(r'.*required.*', headers['X-GitHub-OTP']):
            exception_class = TwoFactorAuthException
        else:
            exception_class = GithubException

        return exception_class(status_code,data)















