################################################################################
#
# python-robolt
#
################################################################################

PYTHON_ROBOLT_VERSION = c4800b27669e511f31f85ac3876e1ae0e288c3b3
PYTHON_ROBOLT_SITE = $(call github,ftCommunity,python-robolt,$(PYTHON_ROBOLT_VERSION))
PYTHON_ROBOLT_LICENSE = MIT
PYTHON_ROBOLT_LICENSE_FILES = LICENSE
PYTHON_ROBOLT_INSTALL_STAGING = NO
PYTHON_ROBOLT_SETUP_TYPE = setuptools
PYTHON_ROBOLT_DEPENDENCIES += python-pyusb

ifeq ($(BR2_PACKAGE_PYTHON),y)
PYTHON_ROBOLT_DEPENDENCIES += python
else ifeq ($(BR2_PACKAGE_PYTHON3),y)
PYTHON_ROBOLT_DEPENDENCIES += python3
endif

$(eval $(python-package))
