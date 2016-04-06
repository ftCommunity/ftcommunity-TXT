################################################################################
#
# python-zbarlight
#
################################################################################

PYTHON_ZBARLIGHT_VERSION = f89d1088e3c8651bee6d851edb4dd927afbac271
PYTHON_ZBARLIGHT_SITE = $(call github,Polyconseil,zbarlight,$(PYTHON_ZBARLIGHT_VERSION))
PYTHON_ZBARLIGHT_LICENSE = MIT
PYTHON_ZBARLIGHT_LICENSE_FILES = LICENSE
PYTHON_ZBARLIGHT_SETUP_TYPE = setuptools

$(eval $(python-package))
