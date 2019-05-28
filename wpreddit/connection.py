import ctypes
import json
import platform
import requests
import time

from wpreddit.common import log


# Checks whether the program can connect to the specified url
# Out: (boolean) connection status for reddit.com
def connected_to_reddit():
    try:
        r = requests.get("http://www.reddit.com/.json?limit=1",
                         headers={'User-Agent': 'wallpaper-reddit python script: ' +
                                                'github.com/markubiak/wallpaper-reddit'},
                         timeout=(3, 10))
        # Connected to something
        if r.status_code != 200:
            return False
        # JSON format, check for 'kind' = "Listing" key
        r_json = json.loads(r.text)
        if r_json['kind'] != "Listing":
            return False
        return True
    except (requests.ConnectionError, requests.ConnectTimeout, AttributeError, ValueError):
        # JSON parsing failed, likely a redirect
        return False


# Waits for a connection to the specified url, or returns False if no connection could be made in the time frame
# In:  (int) number of attempts to connect int
#      (int) interval to retry connection
# Out: (boolean) whether the connection was successfully establised
def wait_for_connection(tries, interval):
    log('Waiting for a connection...')
    for i in range(tries):
        if platform.system() == "Linux":
            # Reloads /etc/resolv.conf
            # credit: http://stackoverflow.com/questions/21356781
            libc = ctypes.cdll.LoadLibrary('libc.so.6')
            res_init = libc.__res_init
            res_init()
        log('Attempt # ' + str(i + 1) + ' to connect...')
        if connected_to_reddit():
            return True
        time.sleep(interval)
    return False
