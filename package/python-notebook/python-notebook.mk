################################################################################
#
# python-notebook
#
################################################################################

PYTHON_NOTEBOOK_VERSION = 4.2.3
PYTHON_NOTEBOOK_SOURCE = notebook-$(PYTHON_NOTEBOOK_VERSION).tar.gz
PYTHON_NOTEBOOK_SITE = https://pypi.python.org/packages/81/a1/20af1a3ea6090343b029d31f882c7e4c061133e0c25808835b1b59a187f8
PYTHON_NOTEBOOK_SETUP_TYPE = distutils
PYTHON_NOTEBOOK_LICENSE = BSD

$(eval $(python-package))
