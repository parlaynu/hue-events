import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from importlib.resources import files


class Client:
    def __init__(self, bridge, user_name, cacertfile):
        self._session = requests.Session()
        self._bridge = bridge

        if user_name is not None:
            self._session.headers.update({"hue-application-key": user_name})

        # try and connect using the hue ca certificate... if it fails, it's because the
        #   bridge is an old one using a self signed certificate so fall back to
        #   not verifying.
        # NOTE: my bridge is the old sort with the self signed certificate... so
        #   I can't be 100% sure that the first part of the sequence below works...
        try:
            self._session.verify = cacertfile
            self.get("/api")
        except requests.exceptions.SSLError:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            self._session.verify = False
            self.get("/api")
                
    def get(self, url, *, extra_headers=None, stream=False, timeout=None):
        full_url = f"https://{self._bridge.address}:{self._bridge.port}{url}"
        return self._session.get(full_url, headers=extra_headers, stream=stream, timeout=timeout)
    
    def post(self, url, *, json=None, extra_headers=None):
        full_url = f"https://{self._bridge}{url}"
        return self._session.post(full_url, json=json)
    
    def close(self):
        self._session.close()


def new_client(bridge, user_name=None):
    cacertfile = files("hlib.resources").joinpath("ca.pem")
    
    cl = Client(bridge, user_name, cacertfile)
    
    return cl

