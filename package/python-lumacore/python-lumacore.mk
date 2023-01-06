################################################################################
#
# python-lumacore
#
################################################################################

PYTHON_LUMACORE_VERSION = 2.4.0
PYTHON_LUMACORE_SOURCE = luma.core-$(PYTHON_LUMACORE_VERSION).tar.gz
PYTHON_LUMACORE_SITE = https://files.pythonhosted.org/packages/b5/d0/dd025f8f665024ec8a0aab928fcb5fb766980f83b1d0127211ccee01054b
PYTHON_LUMACORE_SETUP_TYPE = setuptools
PYTHON_LUMACORE_LICENSE = MIT
PYTHON_LUMACORE_LICENSE_FILES = LICENSE.rst

$(eval $(python-package))
