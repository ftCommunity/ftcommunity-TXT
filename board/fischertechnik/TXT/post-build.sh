#!/bin/sh
TARGET=$1
# copy additional rootfs contents
echo "Adding additional rootfs content ..."
cp -af --remove-destination board/fischertechnik/TXT/rootfs/* $TARGET/
# disable writing log files. On SD card we actually have the space for this, so we can leave this on
# mv $TARGET/etc/init.d/S01logging $TARGET/etc/init.d/M01logging||echo "Logging already turned off!"
# check if user provides custom content
if [ "$FTC_TXT_CUSTOM" != "" ]; then
    echo "Adding user specific content from $FTC_TXT_CUSTOM ..."
    cp -af $FTC_TXT_CUSTOM/* $TARGET/
fi
# Remove obsolete PM firmware load script
rm -f "$TARGET/etc/init.d/S93-am335x-pm-firmware-load"
# Try to generate a detailed firmware version number from git.
# Fall back to the generic version number from the board config
# if we are not building from a git repository, and abort the build
# if we are building from git but the tag part of the version 
# number from git does not match the base version in 
# board/fischertechnik/TXT/rootfs/etc/fw-ver.txt
GIT_VERSION=$(git describe --tags --match='v*' 2>/dev/null)
if [ -n "$GIT_VERSION" ] ; then
  BASE_VERSION=$(cat board/fischertechnik/TXT/rootfs/etc/fw-ver.txt)
  if [ "v$BASE_VERSION" = "${GIT_VERSION%%-*}" ] ; then
    echo ${GIT_VERSION#v*} > $TARGET/etc/fw-ver.txt
  else
    echo "Version number $GIT_VERSION from 'git describe' does not match the base version $BASE_VERSION"
    echo "Please fix the base version in board/fischertechnik/TXT/rootfs/etc/fw-ver.txt"
    exit 1
  fi
fi
echo "done"
