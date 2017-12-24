################################################################################
#
# python-ftrobopy
#
################################################################################

PYTHON_FTDUINO_DIRECT_VERSION = fcc31f1c559c4a80174ee7c49805e3052c35f946
PYTHON_FTDUINO_DIRECT_SITE = $(call github,PeterDHabermehl,ftduino_direct,$(PYTHON_FTDUINO_DIRECT_VERSION))
PYTHON_FTDUINO_DIRECT_LICENSE = GPL-2.0
PYTHON_FTDUINO_DIRECT_LICENSE_FILES = LICENSE
PYTHON_FTDUINO_DIRECT_INSTALL_STAGING = NO
PYTHON_FTDUINO_DIRECT_SETUP_TYPE = distutils
PYTHON_FTDUINO_DIRECT_SUBDIR = python

ifeq ($(BR2_PACKAGE_PYTHON),y)
PYTHON_FTDUINO_DIRECT_DEPENDENCIES += python
else ifeq ($(BR2_PACKAGE_PYTHON3),y)
PYTHON_FTDUINO_DIRECT_DEPENDENCIES += python3
endif

$(eval $(python-package))
