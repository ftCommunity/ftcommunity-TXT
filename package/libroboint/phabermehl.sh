#!/bin/bash

LIBURL=https://github.com/nxdefiant/libroboint/archive/
LIBFILE=0.5.3.zip
IDIR=libroboint-0.5.3

# download libroboint sources
wget $LIBURL$LIBFILE
unzip $LIBFILE

# install libusb-dev
apt-get install libusb-dev
#BR2_PACKAGE_LIBUSB=y
#BR2_PACKAGE_LIBUSB_COMPAT=y
#done

# build
cd $IDIR
cmake .
make
make doc

# install
make install

# install python
make python

#udev rules
cp udev/fischertechnik.rules /etc/udev/rules.d/
#done

# python3 compatibility 'patch'

wget https://github.com/PeterDHabermehl/libroboint-py3/raw/master/robointerface.py
wget https://github.com/PeterDHabermehl/libroboint-py3/raw/master/robointerface.pyc
mv robointerface.py /usr/local/lib/python3.4/dist-packages/
mv robointerface.pyc /usr/local/lib/python3.4/dist-packages/
