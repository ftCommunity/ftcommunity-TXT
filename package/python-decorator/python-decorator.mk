################################################################################
#
# python-decorator
#
################################################################################

PYTHON_DECORATOR_VERSION = 4.0.10
PYTHON_DECORATOR_SOURCE = decorator-$(PYTHON_DECORATOR_VERSION).tar.gz
PYTHON_DECORATOR_SITE = https://pypi.python.org/packages/13/8a/4eed41e338e8dcc13ca41c94b142d4d20c0de684ee5065523fee406ce76f
PYTHON_DECORATOR_SETUP_TYPE = setuptools
PYTHON_DECORATOR_LICENSE = BSD
PYTHON_DECORATOR_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
