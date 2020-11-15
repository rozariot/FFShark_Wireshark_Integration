#!/bin/bash

# A thread safe version of poke.
# This will use flock to create a lock file.
# That way will only run if resource is not currently being used.


(
flock -e 200

dpoke "$@"

#echo "$@"
#sleep 5

) 200>/var/lock/pokelockfile


