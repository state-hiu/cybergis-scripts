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

def make_request(url, params, auth=None, data=None, contentType=None):
    """
    Prepares a request from a url, params, and optionally authentication.
    """
    req = urllib2.Request(url + urllib.urlencode(params), data=data)

    if auth:
        req.add_header('AUTHORIZATION', 'Basic ' + auth)
    
    if contentType:
        req.add_header('Content-type', contentType)
    else:
        if data:
            req.add_header('Content-type', 'text/xml')

    return urllib2.urlopen(req)


def put_file(url, params, auth=None, data=None, contentType=None):


    opener = urllib2.build_opener(urllib2.HTTPHandler)
    
    req = urllib2.Request(url + urllib.urlencode(params), data=data)
    
    if auth:
        req.add_header('AUTHORIZATION', 'Basic ' + auth)
        
    if contentType:
        req.add_header('Content-type', contentType)
    else:
        if data:
            req.add_header('Content-type', 'text/xml')
            
    req.get_method = lambda: 'PUT'
    
    return opener.open(req)

def parse_url(url):
    
    if (url is None) or len(url) == 0:
        return None
    
    index = url.rfind('/')

    if index != (len(url)-1):
        url += '/'
    
    return url

def buildPOSTDataStyle(name,filename):
    file_data ="/opt/cybergis-scripts.git/templates/post_createstyle.xml"
    data = None
    with open (file_data, "r") as f:
        data = f.read().replace('{{name}}', name).replace('{{filename}}', filename)
    return data
    
def readStyleFile(filename):
    data = None
    with open (filename, "r") as f:
        data = f.read()
    return data


def createStyle(verbose, geoserver, auth, name, filename):
    if verbose > 0:
        print('Creating Style...')
    params = {}
    data = buildPOSTDataStyle(name, filename)
    url = geoserver+"rest/styles.json"
    request = make_request(url=url+'?', params=params, auth=auth, data=data)

    print request.getcode()
    if request.getcode() != 201:
        raise Exception("Create style failed: Status Code {0}".format(request.getcode()))

    if verbose > 0:
        print('Style created.')
        
def populateStyle(verbose, geoserver, auth, name, sld):
    if verbose > 0:
        print('Populating style...')
    params = {}
    data = readStyleFile(sld)
    url = geoserver+"rest/styles/"+name+""
    request = put_file(url=url+'?', params=params, auth=auth, data=data, contentType='application/vnd.ogc.sld+xml')

    print request.getcode()
    if request.getcode() != 200:
        raise Exception("Populate style failed: Status Code {0}".format(request.getcode()))

    if verbose > 0:
        print('Style populated.')


def run(args):
    #==#
    verbose = args.verbose
    #==#
    path = args.path
    geoserver = parse_url(args.geoserver)
    prefix = args.prefix
    #==#
    auth = None
    if args.username and args.password:
        auth = b64encode('{0}:{1}'.format(args.username, args.password))
    #==#
    for path_ns in glob.glob(path+os.sep+"*"):
        print "-------------------"
        head_ns, ns = os.path.split(path_ns)
        print "Namespace: "+ns
        for path_sld in glob.glob(path_ns+os.sep+"*.sld"):
            print "Path: "+path_sld
            head,tail = os.path.split(path_sld)
            name, ext = os.path.splitext(tail)
            print "Name: "+name
            #==#
            name_gs = ns+"_"+name
            if prefix:
                name_gs = prefix + name_gs
            try:
              createStyle(verbose,geoserver,auth,name_gs,name_gs+".sld")
            except: 
                print "Error creating style "+name_gs
            
            try:
                populateStyle(verbose,geoserver,auth,name_gs,path_sld)
            except:
                print "Error populating style "+name_gs
            
    
    print "=================================="
