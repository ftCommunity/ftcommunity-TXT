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

# Check if firmware version from the board version and tag match
GIT_VERSION=$(git -C $BR2_EXTERNAL_FTCOMMUNITY_TXT_PATH describe --tags --match='v*' 2>/dev/null)
if [ -n "$GIT_VERSION" ] ; then
  BASE_VERSION=$(cat $BR2_EXTERNAL_FTCOMMUNITY_TXT_PATH/board/fischertechnik/TXT/rootfs/etc/fw-ver.txt)
  if [[ "${GIT_VERSION}" == "v${BASE_VERSION}"* ]] ; then
    echo "v${BASE_VERSION} is a regular release"
  elif [ "${BASE_VERSION#*-}" = "rc" ]; then
    echo "v${BASE_VERSION} is an rc release"
  else
    echo "Version number $GIT_VERSION from 'git describe' does not match the base version $BASE_VERSION"
    echo "Please fix the base version in board/fischertechnik/TXT/rootfs/etc/fw-ver.txt"
    exit 1
  fi
fi
echo "done"
