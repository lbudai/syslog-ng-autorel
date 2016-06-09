import base64
import re
from clients.http_client import HTTPClient
from clients.github_exceptions import (BadCredentialsException,
                                       GithubException,
                                       UserAgentException,
                                       ObjectNotFoundException,
                                       UnprocessableEntityException,
                                       TwoFactorAuthException,
                                       LoginAttemptExceededException,
                                       BadRequestException,
                                       RateLimitExceededException
                                       )


class Github:

    """
        Client interacting with the Github REST API
    """

    def __init__(self, endpoint, port, token_or_login, password, clientID,
                 clientSecret, userAgent, timeout):
        self._headers = {}  # HTTP headers
        self._params = {}  # URL-parameters
        if password is not None:
            # https://developer.github.com/v3/#basic-authentication
            username = token_or_login
            auth_string = username + ":" + password
            self._headers["Authorization"] = "Basic " + \
                base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        elif password is None:
            # https://developer.github.com/v3/#oauth2-token-sent-in-a-header
            self._headers["Authorization"] = "token " + token_or_login
        elif clientID and clientSecret:
            # https://developer.github.com/v3/#oauth2-keysecret
            self._params["client_id"] = clientID
            self._params["client_secret"] = clientSecret
        # Github API requires a user agent, if provided else fallback to what
        # HTTPClient is using
        if userAgent:
            self._headers["User-Agent"] = userAgent
        # Accept only version 3 of the API
        # ( https://developer.github.com/v3/#current-version )
        self._headers["Accept"] = "application/vnd.github.v3+json"
        self._client = HTTPClient(
            endpoint, port, self._headers, self._params, timeout)

    def _doExceptionHandling(self, status_code, headers, data):
        """
            Check the response for possible exceptions
        """
        exception_class = None
        if status_code == 401 and data.get("message") == "Bad credentials":
            exception_class = BadCredentialsException
        elif (status_code == 403 and
              data.get("message").startswith("Maximum number")):
            exception_class = LoginAttemptExceededException
        elif (status_code == 403 and
              data.get("message").startswith("API Rate Limit Exceeded")):
            exception_class = RateLimitExceededException
        elif (status_code == 403 and
              data.get("message").startswith("Missing or invalid User Agent")):
            exception_class = UserAgentException
        elif status_code == 404 and data.get("message") == "Not Found":
            exception_class = ObjectNotFoundException
        elif status_code == 400:
            exception_class = BadRequestException
        elif status_code == 422:
            exception_class = UnprocessableEntityException
        elif (status_code == 401 and "X-GitHub-OTP" in headers and
              re.match(r".*required.*", headers["X-GitHub-OTP"])):
            exception_class = TwoFactorAuthException
        elif str(status_code).startswith("4"):
            exception_class = GithubException
        else:
            return
        raise exception_class(status_code, data)

    def req(self, method="GET", url="", headers={}, params={}, payload={}):
        """
            Make a request using the HTTPClient instance
        """
        (status_code, headers, data) = self._client.carryRequest(
            method, url, headers, params, payload)
        self._doExceptionHandling(status_code, headers, data)
        return data


class GithubInterface:

    """
        Interface to Github API reponse
    """
    def __init__(self, client):
        self._requestor = client

    def getValue(self, **kwargs):
        """
            A method to wrap a single API response
        """
        transform_func = kwargs.pop('transform',None)
        self._request(**kwargs)
        if transform_func:
            return transform_func(**self._data)
        else:
            return self._data

    def getValues(self,**kwargs):
        """
            A method to wrap muliple API repsonses i.e
            a JSON array
        """
        transform_func = kwargs.pop('transform',None)
        self._request(**kwargs)
        if transform_func:
            return [transform_func(**data_element)
                        for data_element in self._data]
        else:
            return self._data

    def _request(self, **kwargs):
        """
            Carry out a request
        """
        method = kwargs.pop("method","GET")
        payload = kwargs.pop("payload",{})
        headers = kwargs.pop("headers",{})
        path_dict = {}
        for path_variable in self._pathVars:
            if path_variable in kwargs:
                path_dict[path_variable] = kwargs.pop(path_variable)
            else:
                raise ValueError(
                    'The method expects a {0} parameter'.format(path_variable))
        # Assemble URL PATH using the path varibale
        path = self._path.format(**path_dict)
        # Remaining keywords are used to make URL parameters
        params = kwargs
        # Cook the request
        self._data = self._requestor.req(method=method,
                                         url=path,
                                         headers=headers,
                                         params=params,
                                         payload=payload
                                         )
