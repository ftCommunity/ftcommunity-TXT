################################################################################
#
# python-robolt
#
################################################################################

PYTHON_ROBOLT_VERSION = 06817329abcee294d08f62efbbf951cad1bcaae0
PYTHON_ROBOLT_SITE = $(call github,ftCommunity,python-robolt,$(PYTHON_ROBOLT_VERSION))
PYTHON_ROBOLT_LICENSE = MIT
PYTHON_ROBOLT_LICENSE_FILES = LICENSE
PYTHON_ROBOLT_INSTALL_STAGING = NO
PYTHON_ROBOLT_SETUP_TYPE = distutils
PYTHON_ROBOLT_DEPENDENCIES += libusb

ifeq ($(BR2_PACKAGE_PYTHON),y)
PYTHON_ROBOLT_DEPENDENCIES += python
else ifeq ($(BR2_PACKAGE_PYTHON3),y)
PYTHON_ROBOLT_DEPENDENCIES += python3
endif

$(eval $(python-package))
