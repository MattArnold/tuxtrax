#!/bin/bash 

BASEDIR=$(dirname $0)
cd $BASEDIR/soci-3.2.2
mkdir build
cd build
cmake -G "Unix Makefiles" -DWITH_BOOST=OFF ../
make
cd ../../
make
cd ../