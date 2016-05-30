import requests
import json
import sys

__pyversion__ = sys.version_info[0]
if __pyversion__ == 2: # Python2
    from urlparse import urljoin
else: # Python3
    from urllib.parse import urljoin

DEFAULT_HEADERS = {
    'User-Agent' : 'syslog-ng-autorel',
    'From' : 'ankprashar@gmail.com',
    "Origin": 'black-perl.in'
}

DEFAULT_TIMEOUT = 30

class BaseClient(object):
    '''
        A Base HTTP client
    '''
    http_methods = (
        'head',
        'get',
        'post',
        'put',
        'patch',
        'delete',
    )

    def __init__(self,endpoint,port,timeout=None):
        '''
            The Constructor method for a generic client. 
        '''
        self._endpoint = endpoint
        self._port = port
        self._timeout = timeout if timeout else DEFAULT_TIMEOUT
        self._headers = DEFAULT_HEADERS

    def carryRequest(self,method='GET',url='',headers={},params={},payload={}):
        '''
        Carry out a {method} request.
        - The url can be a FQDN( Fully qualified Performmain name ) but should have netloc same as that
          of API endpoint.
        '''
        method = method.lower()
        methodToCall = getattr(requests,method)
        request_url = url if url.startswith('http') else urljoin(self._endpoint,url)
        self._headers.update(headers)
        headers = self._headers
        timeout = self._timeout
        try:
            if method == 'post' or method == 'put':
                # encode the payload to json if required
                if headers['Content-Type'] == 'application/json':
                    data = json.dumps(payload)
                # the payload will automatically be form-encoded
                else:
                    data = payload
                result = methodToCall(request_url,
                                      headers=headers,
                                      params=params,
                                      data=data,
                                      timeout=timeout,
                                      verify=False)
            else:
                result = methodToCall(request_url,
                                      headers=headers,
                                      params=params,
                                      data=payload,
                                      timeout=timeout)
        except Exception as e:
            # handle exception, well pass for now
            pass


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



