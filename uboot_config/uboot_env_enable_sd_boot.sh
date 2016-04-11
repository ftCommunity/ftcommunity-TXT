#!/bin/sh
echo "Enabling SD boot"
fw_setenv bootcmd "run sdboot;run nandboot"
