#!/bin/bash
#This script is a work in development and is not stable.
#This script requires curl and git to be installed
#Run this script using root's login shell under: sudo su -

DATE=$(date)

INIT_CMD=$1

#==================================#

add_swap(){
  echo "add_swap"
  if [[ $# -ne 3 ]]; then
    echo "Usage: cybergis-script-ec2.sh swap <size> <file>"
  else
    INIT_ENV=$1
    INIT_CMD=$2
    SIZE=$3
    FILE=$4
    #
    fallocate -l $SIZE $FILE
    chmod 600 $FILE
    mkswap $FILE
    swapon $FILE
  fi
}
delete_swap(){
  echo "delete_swap"
  if [[ $# -ne 2 ]]; then
    echo "Usage: cybergis-script-ec2.sh delete_swap <file>"
  else
    INIT_ENV=$1
    INIT_CMD=$2
    FILE=$3
    #
    swapoff $FILE
    rm $FILE
  fi
}

resize_volume(){
  echo "resize_volume"
  if [[ $# -ne 2 ]]; then
    echo "Usage: cybergis-script-ec2.sh resize <dev>"
  else
    INIT_ENV=$1
    INIT_CMD=$2
    DEVICE=$3
    #
    e2fsck -f $DEVICE
    resize2fs $DEVICE
  fi
}

if [[ "$INIT_CMD" == "resize" ]]; then
        
    if [[ $# -ne 3 ]]; then
        echo "Usage: cybergis-script-ec2.sh $INIT_CMD"
    else
        export -f resize_volume
        bash --login -c "resize_volume $INIT_CMD '${3}'"
    fi
    
elif [[ "$INIT_CMD" == "swap" ]]; then
    
    if [[ $# -ne 4 ]]; then
        echo "Usage: cybergis-script-ec2.sh $INIT_CMD <size> <file>"
    else
        export -f add_swap
        bash --login -c "add_swap $INIT_CMD '${3}' '${4}'"
    fi
    
elif [[ "$INIT_CMD" == "delete_swap" ]]; then
    
    if [[ $# -ne 3 ]]; then
        echo "Usage: cybergis-script-ec2.sh $INIT_CMD <file>"
    else
        export -f delete_swap
        bash --login -c "delete_swap $INIT_CMD '${3}'"
    fi
    
else
    echo "Usage: cybergis-script-ec2.sh [resize|swap|delete_swap]"
fi
