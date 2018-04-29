################################################################################
#
# python-wedo
#
################################################################################

PYTHON_WEDO_VERSION = 1085c6288fd8993193deda24fa3b7c8c62ee3727
PYTHON_WEDO_SITE = $(call github,itdaniher,WeDoMore,$(PYTHON_WEDO_VERSION))
PYTHON_WEDO_LICENSE = MIT
PYTHON_WEDO_LICENSE_FILES = LICENSE
PYTHON_WEDO_INSTALL_STAGING = NO
PYTHON_WEDO_SETUP_TYPE = setuptools
PYTHON_WEDO_DEPENDENCIES += python-pyusb

ifeq ($(BR2_PACKAGE_PYTHON),y)
PYTHON_WEDO_DEPENDENCIES += python
else ifeq ($(BR2_PACKAGE_PYTHON3),y)
PYTHON_WEDO_DEPENDENCIES += python3
endif

$(eval $(python-package))
