import requests
import json
from urllib.parse import urljoin

DEFAULT_HEADERS = {
    'User-Agent' : 'syslog-ng-autorel',
    'From' : 'ankprashar@gmail.com',
    "Origin": 'black-perl.in'
}

DEFAULT_TIMEOUT = 30


class HTTPClient(object):
    '''
        A HTTP client
    '''
    http_methods = (
        'head',
        'get',
        'post',
        'put',
        'delete',
    )
    # Terminal debugging vars 
    DEBUG_FLAG = False
    DEBUG_FRAME_BUFFER_SIZE = 1024
    DEBUG_HEADER_KEY = "DEBUG_FRAME" # Points to the frame in the buffer

    def __init__(self,endpoint,port,headers,params,timeout=None):
        '''
            The Constructor method for a generic client. 
        '''
        self._endpoint = endpoint
        self._port = port
        self._timeout = timeout if timeout else DEFAULT_TIMEOUT
        self._headers = DEFAULT_HEADERS
        self._headers.update(headers)
        self._params = params
        self._startDebugging()

    def _startDebugging(self):
        '''
            Initialise debugging varss
        '''
        if self.DEBUG_FLAG:
            self._frameCount = -1 # Performs the index keeping of the last injected debug frame
            self._frameBuffer = [] # Debug frames storage

    def NEW_DEBUG_FRAME(self,reqHeaders):
        '''
            Initialize a debug frame with requestHeaders
            Frame count is updated and will be attached to respond header
            The structure of a frame: [requestHeader, statusCode, responseHeader, raw_data]
            - Some of them takes None value for now
        '''
        if self.DEBUG_FLAG: # Debug only when the debug flag is set
            new_frame = [reqHeaders,None,None,None]
            if self._frameCount < self.FRAME_BUFFER_SIZE-1:
                self._frameBuffer.append(new_frame)
            else:
                self._frameCount = -1
                self._frameBuffer[0] = new_frame
            self._frameCount += 1

    def DEBUG_ON_RESPONSE(self,respHeader,respStatus,respData):
        '''
            Add the API response to the debug frame
        '''
        if self.DEBUG_FLAG: # Debug only when the debug flag is set
            self._frameBuffer[1:4] = [respHeader,respStatus,respData]
            self._frameBuffer[self.DEBUG_HEADER_KEY] = self._frameCount

    def DEBUG_LOGGING(self):
        if self.DEBUG_LOGGING:
            # log the frames to the terminal, pass for now
            pass

    def carryRequest(self,method='GET',url='',headers={},params={},payload={}):
        '''
        Carry out a {method} request.
        - The url can be a FQDN( Fully qualified Performmain name ) but should have netloc same as that
          of API endpoint.
        '''
        method = method.lower()
        self._makeConnection()
        methodToCall = getattr(requests,method)
        request_url = url if url.startswith('http') else urljoin(self._endpoint,url)
        headers.update(self._headers)
        params.update(self._params)
        timeout = self._timeout
        self.NEW_DEBUG_FRAME(headers)
        try:
            if method == 'post' or method == 'put':
                # encode the payload to json if required
                if headers['Content-Type'] == 'application/json':
                    data = json.dumps(payload)
                # the payload will be automatically form-encoded elsewise
                else:
                    data = payload
                resp = methodToCall(request_url,headers=headers,params=params,data=data,timeout=timeout,verify=False)
            else:
                resp = methodToCall(request_url,headers=headers,params=params,data=payload,timeout=timeout)
            # Debug on response
            self.DEBUG_ON_RESPONSE(resp.headers,resp.status_code,resp.json())
            # Github API always returns a JSON (https://developer.github.com/v3/#schema)
            # resp.json() is safe, it won't throw a JSONDecodingError
            return (resp.status_code,resp.headers,resp.json())
        except Exception as e:
            # Cases where there is no any HTTP Error, Client Errors
            raise ClientException(e)



    def get(self,url='',headers={},params={}):
        '''
            Performs a GET request
        '''
        return self.makeRequest('get',url,headers,params)

    def head(self,url='',headers={},params={}):
        '''
            Performs a HEAD request
        '''
        return self.makeRequest('head',url,headers,params)

    def post(self,url='',headers={},params={},payload={}):
        '''
            Performs a POST request
        '''
        return self.makeRequest('post',url,headers,params,payload)

    def put(self,url='',headers={},params={},payload={}):
        '''
            Performs a PUT request
        '''
        return self.makeRequest('put',url,headers,params,payload)

    def delete(self,url='',headers={},params={}):
        '''
            Performs a DELETE request
        '''
        return self.makeRequest('delete',url,headers,params)


class ClientException(Exception):
    '''
        Throws Exception in case of Networking Errors
        - e error_object
    '''
    def __init__(self,e):
        Exception._init__(self)
        self._errorObj = e

    def __str__(self):
        return "ClientException" + " " + str(self._errorObj)