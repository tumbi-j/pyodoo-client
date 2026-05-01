import requests
from .http_adapter import HttpAdapter

class RequestsHttpAdapter(HttpAdapter):
    def __init__(self, session: requests.Session):
        self.session = session
    
    def post(self, url, json=None, headers=None, timeout=None, verify=True):
        return self.session.post(url, json=json, headers=headers, timeout=timeout, verify=verify)

    def request(self, method, url, json=None, data=None, files=None, headers=None, timeout=None, verify=True):
        return self.session.request(
            method=method,
            url=url,
            json=json,
            data=data,
            files=files,
            headers=headers,
            timeout=timeout,
            verify=verify,
        )