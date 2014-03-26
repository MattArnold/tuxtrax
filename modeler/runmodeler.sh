#!/bin/bash

BASEDIR=$(dirname $0)
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$BASEDIR/soci-3.2.2/build/lib
$BASEDIR/bin/modeler $1 $2 $3 $3 $4 $5 $6 $7 $7 $9