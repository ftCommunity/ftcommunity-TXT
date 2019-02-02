################################################################################
#
# python-ftframework
#
################################################################################

PYTHON_FTFRAMEWORK_VERSION = v1.0.0
PYTHON_FTFRAMEWORK_SITE = $(call github,ski7777,ftframework,$(PYTHON_FTFRAMEWORK_VERSION))
PYTHON_FTFRAMEWORK_LICENSE = GPL-3.0
PYTHON_FTFRAMEWORK_LICENSE_FILES = LICENSE
PYTHON_FTFRAMEWORK_SETUP_TYPE = setuptools
PYTHON_FTFRAMEWORK_DEPENDENCIES = python-twisted

$(eval $(python-package))
