################################################################################
#
# python-ftrobopy
#
################################################################################

PYTHON_FTDUINO_DIRECT_VERSION = 9034dc899599106aaa1284cefda0bb6e4e5b8b36
PYTHON_FTDUINO_DIRECT_SITE = $(call github,PeterDHabermehl,ftduino_direct,$(PYTHON_FTDUINO_DIRECT_VERSION))
PYTHON_FTDUINO_DIRECT_LICENSE = GPL-2.0
PYTHON_FTDUINO_DIRECT_LICENSE_FILES = LICENSE
PYTHON_FTDUINO_DIRECT_INSTALL_STAGING = NO
PYTHON_FTDUINO_DIRECT_SETUP_TYPE = distutils
PYTHON_FTDUINO_DIRECT_SUBDIR = python
PYTHON_FTDUINO_DIRECT_DEPENDENCIES = python-serial

ifeq ($(BR2_PACKAGE_PYTHON),y)
PYTHON_FTDUINO_DIRECT_DEPENDENCIES += python
else ifeq ($(BR2_PACKAGE_PYTHON3),y)
PYTHON_FTDUINO_DIRECT_DEPENDENCIES += python3
endif

$(eval $(python-package))
