################################################################################
#
# python-ftifpy
#
################################################################################

PYTHON_FTIFPY_VERSION = 1.0.0
PYTHON_FTIFPY_SITE = $(call github,ski7777,ftifpy,$(PYTHON_FTIFPY_VERSION))
PYTHON_FTIFPY_LICENSE = GPL-3.0
PYTHON_FTIFPY_DEPENDENCIES = python-libroboint
PYTHON_FTIFPY_LICENSE_FILES = LICENSE
PYTHON_FTIFPY_INSTALL_STAGING = NO
PYTHON_FTIFPY_SETUP_TYPE = distutils

$(eval $(python-package))
