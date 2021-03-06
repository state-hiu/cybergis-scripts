#!/bin/bash
#=================#
#Based on scripts from https://github.com/ROGUE-JCTD/rogue-scripts
#=================#
DATE=$(date)
CTX_GEOGIG="/geoserver/geogig/"
GEONODE_LOCAL="http://localhost"
PYTHON=/var/lib/geonode/bin/python
#MANAGE=/var/lib/geonode/rogue_geonode/manage.py
DIR=/var/lib/geonode/rogue_geonode
#==#
# Auto-Sync Delay (in seconds)
AUTO_SYNC_DELAY=60
# Sync Attempts
SYNC_ATTEMPTS=10
# This will track whether or not an error occurred
ERROR_OCCURED=0
#=================#
if [[ $# -ne 6 ]]; then
    echo "Usage: geogig_sync_osm.sh <repo> <remote> <authorname> <authoremail> <log_file> <error_file>"
    echo 'authorname and authoremail used when merging non-conflicting branches'
    echo 'repo points to the staging repo'
    echo 'remote points to the live repo to be updated'
else
    REPO=$1
    REMOTE=$2
    AUTHORNAME=$3
    AUTHOREMAIL=$4
    LOG_FILE=$5
    ERROR_FILE=$6
    #=================#
    cd $REPO
    #=================#
    if [ -f $ERROR_FILE ]; then
        exit 255
    fi
    #=================#
    exec 1>$LOG_FILE
    #=================#
    printf "\nUpdating OSM Data...";
    printf "\n===========================\n";
    geogig checkout master
    geogig osm download --update
    geogig checkout master
    #=================#
    printf "\n===========================";
    printf "\nSynchronizing repository...";
    printf "\n===========================\n";
    for i in `seq 1 $SYNC_ATTEMPTS`
    do
	echo "Attempt $i of $SYNC_ATTEMPTS."
        ERROR_OCCURED=0
	geogig pull $REMOTE
        EXIT_CODE=$?
        if [ $EXIT_CODE -gt 0 ]; then
         ERROR_OCCURED=255
        fi
        OUTPUT=$(geogig push $REMOTE)
        EXIT_CODE=$?
        echo $OUTPUT
        if [ $EXIT_CODE -gt 0 ]; then 
            if [  "$OUTPUT" != "Nothing to push." ]; then
                ERROR_OCCURED=255
            fi
        fi
	if [ $ERROR_OCCURED -eq 0 ]; then
         break
	fi
        sleep $AUTO_SYNC_DELAY
    done
    
    if [ $ERROR_OCCURED -eq 255 ]; then
        #cat $LOG_FILE | mail -s "$EMAIL_SUBJECT" $EMAIL_ADDRESS
        echo $ERROR_MESSAGE >> $ERROR_FILE
    fi
fi
