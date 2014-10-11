from base64 import b64encode
from optparse import make_option
import json
import urllib
import urllib2
import argparse
import time
import os
import subprocess
import glob

def make_request(url, params, auth=None, data=None):
    """
    Prepares a request from a url, params, and optionally authentication.
    """
    req = urllib2.Request(url + urllib.urlencode(params), data=data)

    if auth:
        req.add_header('AUTHORIZATION', 'Basic ' + auth)
    if data:
        req.add_header('Content-type', 'text/xml')

    return urllib2.urlopen(req)

def parse_url(url):
    
    if (url is None) or len(url) == 0:
        return None
    
    index = url.rfind('/')

    if index != (len(url)-1):
        url += '/'
    
    return url


def run(args):
    #print args
    #==#
    verbose = args.verbose
    #==#
    path = args.path
    geoserver = parse_url(args.geoserver)
    #==#
    
    
    
    print "=================================="
