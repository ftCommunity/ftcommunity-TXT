################################################################################
#
# python-wedo
#
################################################################################

PYTHON_WEDO_VERSION = 2d1963a74a50b3f6b35a8de44891bd0424a02a07
PYTHON_WEDO_SITE = $(call github,itdaniher,WeDoMore,$(PYTHON_WEDO_VERSION))
PYTHON_WEDO_LICENSE = MIT
PYTHON_WEDO_LICENSE_FILES = LICENSE
PYTHON_WEDO_INSTALL_STAGING = NO
PYTHON_WEDO_SETUP_TYPE = distutils
PYTHON_WEDO_DEPENDENCIES += libusb

ifeq ($(BR2_PACKAGE_PYTHON),y)
PYTHON_WEDO_DEPENDENCIES += python
else ifeq ($(BR2_PACKAGE_PYTHON3),y)
PYTHON_WEDO_DEPENDENCIES += python3
endif

$(eval $(python-package))
