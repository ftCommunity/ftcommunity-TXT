################################################################################
#
# python-nbformat
#
################################################################################

PYTHON_NBFORMAT_VERSION = 4.1.0
PYTHON_NBFORMAT_SOURCE = nbformat-$(PYTHON_NBFORMAT_VERSION).tar.gz
PYTHON_NBFORMAT_SITE = https://pypi.python.org/packages/c5/b5/f38ceeeac63e9b4d7d630151be8875beb3d4a86eba5b5ad9d3dbefadadea
PYTHON_NBFORMAT_SETUP_TYPE = distutils
PYTHON_NBFORMAT_LICENSE = BSD

$(eval $(python-package))
