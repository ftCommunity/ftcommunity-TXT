################################################################################
#
# python-websockets
#
################################################################################

PYTHON_WEBSOCKETS_VERSION = fbc218ea93288e56dd7b55f69186392844171c5c
PYTHON_WEBSOCKETS_SITE = $(call github,aaugustin,websockets,$(PYTHON_WEBSOCKETS_VERSION))
PYTHON_WEBSOCKETS_LICENSE = MIT
PYTHON_WEBSOCKETS_LICENSE_FILES = LICENSE
PYTHON_WEBSOCKETS_INSTALL_STAGING = NO
PYTHON_WEBSOCKETS_SETUP_TYPE = setuptools

ifeq ($(BR2_PACKAGE_PYTHON),y)
PYTHON_WEBSOCKETS_DEPENDENCIES += python
else ifeq ($(BR2_PACKAGE_PYTHON3),y)
PYTHON_WEBSOCKETS_DEPENDENCIES += python3
endif

$(eval $(python-package))
