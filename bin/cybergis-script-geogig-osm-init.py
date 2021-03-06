#!/usr/bin/python
from base64 import b64encode
from optparse import make_option
import json
import urllib
import urllib2
import argparse
import time
import os
import sys
import subprocess
#==#
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib', 'cybergis')))
import gg._geogig_init_repo
import gg._geogig_sync_osm
#==#
class ov(object):
    def __init__(self, d):
        self.__dict__ = d
        
def run(args):
    #print args
    #==#
    verbose = args.verbose
    #==
    authorname = args.authorname
    authoremail = args.authoremail
    #==#
    name = args.name
    geoserver = args.geoserver
    path = args.path
    parent = args.parent
    datastore = args.datastore
    workspace = args.workspace
    timeout = args.timeout
    #==#
    username = args.username
    password = args.password
    #==#
    extents = args.extents
    mapping = args.mapping
    #==#
    include_nodes = args.nodes
    include_ways = args.ways
    #==#
    extracts = args.extracts
    #==#
    print "=================================="
    print "#==#"
    print "CyberGIS Script / geogig_init_extract.py"
    print "Initialize GeoGig repository, adds to GeoServer, downloads OSM extract, publishes layers"
    print "#==#"
    #==#
    print "Executing subroutines"
    gg._geogig_init_repo.run(ov({
        'parent': parent,
        'path': path,
        'name': name,
        'datastore': datastore,
        'geoserver': geoserver,
        'workspace': workspace,
        'create_repo': 1,
        'publish_datastore': 1,
        'publish_layers': 0,
        'username': username,
        'password': password,
        'verbose': verbose,
        'nodes': 0,
        'ways': 0,
        'extracts': extracts
    }))
    #==#
    gg._geogig_sync_osm.run(ov({
        'update': 'false',
        'repo':None,
        'datastore': datastore,
        'geoserver': geoserver,
        'workspace': workspace,
        'username': username,
        'password': password,
        'verbose': verbose,
        'authorname':authorname,
        'authoremail': authoremail,
        'extents': extents,
        'mapping': mapping,
        'timeout': timeout,
        'extracts': extracts
    }))
    #==#
    gg._geogig_init_repo.run(ov({
        'parent': parent,
        'path': None,
        'name': name,
        'datastore': datastore,
        'geoserver': geoserver,
        'workspace': workspace,
        'create_repo': 0,
        'publish_datastore': 0,
        'publish_layers': 1,
        'username': username,
        'password': password,
        'verbose': verbose,
        'nodes': include_nodes,
        'ways': include_ways,
        'extracts': extracts
    }))                    
    print "=================================="

parser = argparse.ArgumentParser(description='Initialize GeoGig repository and optionally add to GeoServer instance.  If you want to add the GeoGig repo include the optional parameters.')
parser.add_argument("--path", help="The location in the filesystem of the GeoGig repositories.")
parser.add_argument("--parent", help="The location in the filesystem that is parent to GeoGig repositories.")
parser.add_argument("--name", help="The name of the GeoGig repo within the file system.")
parser.add_argument('-ds', '--datastore', help="The name of the GeoGig datastore in GeoServer.")
parser.add_argument('-gs', '--geoserver', help="The url of the GeoServer servicing the GeoGig repository.")
parser.add_argument('-ws', '--workspace', help="The GeoServer workspace to use for the data store.")
parser.add_argument("--username", help="The username to use for basic auth requests.")
parser.add_argument("--password", help="The password to use for basic auth requests.")
parser.add_argument('--verbose', '-v', default=0, action='count', help="Print out intermediate status messages.")
parser.add_argument('-an', '--authorname', help="The author name to use when merging non-conflicting branches.")
parser.add_argument('-ae', '--authoremail', help="The author email to use when merging non-conflicting branches.")
parser.add_argument('--extracts', help="A tab seperated file (TSV) specifying the datastore, extent, and mapping for each extract.")
parser.add_argument("--extents", help="The extents of the OpenStreetMap extract. For example, dominican_republic:santo_domingo or guinea:guiea;liberia:liberia.")
parser.add_argument("--mapping", help="The mapping of the OpenStreetMap extract.  For example, basic:bulding_and_roads.")
parser.add_argument('-to', '--timeout', type=int, default=30, help="The number of seconds to wait for the osm download task to complete before cancelling.  Default is 30 seconds.")
parser.add_argument('--nodes', default=0, action='count', help="If publishing layers, include nodes.")
parser.add_argument('--ways', default=0, action='count', help="If publishing layers, include ways.")
args = parser.parse_args()
#==#
run(args)
