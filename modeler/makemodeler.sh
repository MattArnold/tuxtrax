#!/bin/bash 

FILE=$(readlink -f $0)
BASEDIR=`dirname $FILE`
cd $BASEDIR/cmake-2.8.12.2
./bootstrap
make
cd $BASEDIR/soci-3.2.2
mkdir build
cd build
export PATH=$PATH:$BASEDIR/cmake-2.8.12.2/bin
cmake -G "Unix Makefiles" -DWITH_BOOST=OFF ../
make
cd ../../
make
cd ../