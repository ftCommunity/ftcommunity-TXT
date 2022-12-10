################################################################################
#
# python-zbarlight
#
################################################################################

PYTHON_ZBARLIGHT_VERSION = 3.0
PYTHON_ZBARLIGHT_SITE = $(call github,Polyconseil,zbarlight,$(PYTHON_ZBARLIGHT_VERSION))
PYTHON_ZBARLIGHT_LICENSE = MIT
PYTHON_ZBARLIGHT_LICENSE_FILES = LICENSE
PYTHON_ZBARLIGHT_SETUP_TYPE = setuptools
PYTHON_ZBARLIGHT_DEPENDENCIES += zbar

$(eval $(python-package))
