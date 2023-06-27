#!/bin/bash
TARGET=$1
cp -af $BR2_EXTERNAL_FTCOMMUNITY_TXT_PATH/docs/favicon.ico $TARGET/var/www/
# disable writing log files. On SD card we actually have the space for this, so we can leave this on
# mv $TARGET/etc/init.d/S01logging $TARGET/etc/init.d/M01logging||echo "Logging already turned off!"
# Remove obsolete PM firmware load script
rm -f "$TARGET/etc/init.d/S93-am335x-pm-firmware-load"

# remove start scripts for openvpn
rm -f "$TARGET/etc/init.d/S60openvpn"

# remove xorg start script
rm -f "$TARGET/etc/init.d/S40xorg"

# remove unused firmware
find "$TARGET/usr/lib/firmware/ti-connectivity" -iname "TIInit*.bts" ! -name "TIInit_11.8.32.bts" -type f -exec rm -f {} +
find "$TARGET/usr/lib/firmware/ti-connectivity" -iname "wl*.bin" ! -name "wl18xx-fw-4.bin" ! -name "wl18xx-conf.bin" -exec rm -f {} +

# Try to generate a detailed firmware version number from git.
# Fall back to the generic version number from the board config
# if we are not building from a git repository, and abort the build
# if we are building from git but the tag part of the version
# number from git does not match the base version in 
# board/fischertechnik/TXT/rootfs/etc/fw-ver.txt
GIT_VERSION=$(git -C $BR2_EXTERNAL_FTCOMMUNITY_TXT_PATH describe --tags --match='v*' 2>/dev/null)
if [ -n "$GIT_VERSION" ] ; then
  BASE_VERSION=$(cat $BR2_EXTERNAL_FTCOMMUNITY_TXT_PATH/board/fischertechnik/TXT/rootfs/etc/fw-ver.txt)
  if [[ "${GIT_VERSION}" == "v${BASE_VERSION}"* ]] ; then
    echo "${GIT_VERSION#v}" > $TARGET/etc/fw-ver.txt
  elif [ "${BASE_VERSION#*-}" = "rc" ]; then
    echo "${BASE_VERSION}+${GIT_VERSION}" > $TARGET/etc/fw-ver.txt
  else
    echo "Version number $GIT_VERSION from 'git describe' does not match the base version $BASE_VERSION"
    echo "Please fix the base version in board/fischertechnik/TXT/rootfs/etc/fw-ver.txt"
    exit 1
  fi
fi
echo "done"
