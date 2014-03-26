#!/bin/bash

FILE=$(readlink -f $0)
BASEDIR=`dirname $FILE`
TMPDIR=$BASEDIR/../tmp

# Make temp directory
if [ ! -d "$TMPDIR" ]
then
	mkdir $TMPDIR
fi

# Check for cmake file
if [ ! -f "$TMPDIR/cmake-2.8.12.2.tar.gz" ]
then
	curl http://www.cmake.org/files/v2.8/cmake-2.8.12.2.tar.gz > $TMPDIR/cmake-2.8.12.2.tar.gz
fi

# Check for cmake source
if [ ! -d "$BASEDIR/cmake-2.8.12.2" ]
then
	tar xvfz $TMPDIR/cmake-2.8.12.2.tar.gz -C $BASEDIR
fi

# Check for soci file
if [ ! -f "$TMPDIR/soci-3.2.2.tar.gz" ]
then
	curl -L http://sourceforge.net/projects/soci/files/soci/soci-3.2.2/soci-3.2.2.tar.gz > $TMPDIR/soci-3.2.2.tar.gz
fi

# Check for soci source
if [ ! -d "$BASEDIR/soci-3.2.2" ]
then
	tar xvfz $TMPDIR/soci-3.2.2.tar.gz -C $BASEDIR
fi

# Check for sqlite3 file
if [ ! -f "$TMPDIR/sqlite-autoconf-3080401.tar.gz" ]
then
	curl http://sqlite.org/2014/sqlite-autoconf-3080401.tar.gz > $TMPDIR/sqlite-autoconf-3080401.tar.gz
fi

# Check for sqlite3 source
if [ ! -d "$BASEDIR/sqlite-autoconf-3080401" ]
then
	tar xvfz $TMPDIR/sqlite-autoconf-3080401.tar.gz -C $BASEDIR
fi

# Make cmake
cd $BASEDIR/cmake-2.8.12.2
if [ ! -d "$BASEDIR/cmake-2.8.12.2/Bootstrap.cmk" ]
then
	./bootstrap
fi
make

# Make sqlite3
cd $BASEDIR/sqlite-autoconf-3080401
if [ ! -f "$BASEDIR/sqlite-autoconf-3080401/Makefile" ]
then
	./configure --disable-static CFLAGS="-g -O2 -DSQLITE_ENABLE_FTS3=1 -DSQLITE_ENABLE_COLUMN_METADATA=1 -DSQLITE_ENABLE_UNLOCK_NOTIFY=1 -DSQLITE_SECURE_DELETE=1"
fi
make

# Make soci
cd $BASEDIR/soci-3.2.2
mkdir build
cd build
export PATH=$PATH:$BASEDIR/cmake-2.8.12.2/bin
cmake -G "Unix Makefiles" -DWITH_BOOST=OFF -DSQLITE3_FOUND=ON -DSQLITE3_LIBRARY=$BASEDIR/sqlite-autoconf-3080401/.libs/libsqlite3.so -DSQLITE3_LIBRARIES=$BASEDIR/sqlite-autoconf-3080401/.libs/libsqlite3.so -DSQLITE3_INCLUDE_DIR=$BASEDIR/sqlite-autoconf-3080401 ../
make
cd ../../

# Create output directories
if [ ! -d "$BASEDIR/bin" ]
then
	mkdir $BASEDIR/bin
fi
if [ ! -d "$BASEDIR/obj" ]
then
	mkdir $BASEDIR/obj
fi

# Make modeler
make

# Return to root directory
cd ../
