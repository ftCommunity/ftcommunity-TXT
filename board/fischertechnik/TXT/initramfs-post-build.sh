#!/bin/bash
TARGET=$1
# Remove heavy unneeded files from initramfs target
rm -rf "$TARGET/etc/udev" "$TARGET/usr/lib/udev"
rm -rf "$TARGET/usr/lib/locale"
rm -rf "$TARGET/usr/lib/libstdc++"* "$TARGET/usr/lib/libgfortran"*
rm -rf "$TARGET/usr/bin/gdbserver"
rm -rf "$TARGET/usr/share"
