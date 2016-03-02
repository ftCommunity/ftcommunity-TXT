#!/bin/sh
TARGET=$1
# copy additional rootfs contents
echo "Adding additional rootfs content ..."
cp -af board/knobloch/TXT/rootfs/* $TARGET/
# disable writing log files. On SD card we actually have the space for this, so we can leave this on
# mv $TARGET/etc/init.d/S01logging $TARGET/etc/init.d/M01logging||echo "Logging already turned off!"
# check if user provides custom content
if [ "$FTC_TXT_CUSTOM" != "" ]; then
    echo "Adding user specific content from $FTC_TXT_CUSTOM ..."
    cp -af $FTC_TXT_CUSTOM/* $TARGET/
fi
echo "done"
