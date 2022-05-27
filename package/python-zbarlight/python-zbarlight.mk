################################################################################
#
# python-zbarlight
#
################################################################################

PYTHON_ZBARLIGHT_VERSION = 223eb80aea0ab887625b5b629360f0928e75f77d
PYTHON_ZBARLIGHT_SITE = $(call github,Polyconseil,zbarlight,$(PYTHON_ZBARLIGHT_VERSION))
PYTHON_ZBARLIGHT_LICENSE = MIT
PYTHON_ZBARLIGHT_LICENSE_FILES = LICENSE
PYTHON_ZBARLIGHT_SETUP_TYPE = setuptools
PYTHON_ZBARLIGHT_DEPENDENCIES += zbar

$(eval $(python-package))
