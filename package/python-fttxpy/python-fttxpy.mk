################################################################################
#
# python-fttxpy
#
################################################################################

PYTHON_FTTXPY_VERSION = 0.9.1
PYTHON_FTTXPY_SITE = $(call github,ski7777,fttxpy,$(PYTHON_FTTXPY_VERSION))
PYTHON_FTTXPY_LICENSE = GPL-3.0
PYTHON_FTTXPY_DEPENDENCIES = python-pyudev
PYTHON_FTTXPY_LICENSE = MIT
PYTHON_FTTXPY_LICENSE_FILES = LICENSE
PYTHON_FTTXPY_INSTALL_STAGING = NO
PYTHON_FTTXPY_SETUP_TYPE = distutils

$(eval $(python-package))
