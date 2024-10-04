################################################################################
#
# python-ftrobopy
#
################################################################################

PYTHON_FTROBOPY_VERSION = 3b072b2b6cc352f3c3b627fbe180e4f6b6dddd3b
PYTHON_FTROBOPY_SITE = $(call github,ftrobopy,ftrobopy,$(PYTHON_FTROBOPY_VERSION))
PYTHON_FTROBOPY_LICENSE = MIT
PYTHON_FTROBOPY_LICENSE_FILES = LICENSE
PYTHON_FTROBOPY_INSTALL_STAGING = NO
PYTHON_FTROBOPY_SETUP_TYPE = setuptools
PYTHON_FTROBOPY_DEPENDENCIES = python-serial

ifeq ($(BR2_PACKAGE_PYTHON),y)
PYTHON_FTROBOPY_DEPENDENCIES += python
else ifeq ($(BR2_PACKAGE_PYTHON3),y)
PYTHON_FTROBOPY_DEPENDENCIES += python3
endif

$(eval $(python-package))
