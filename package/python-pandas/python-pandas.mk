################################################################################
#
# python-pandas
#
################################################################################

PYTHON_PANDAS_VERSION = 0.25.3
PYTHON_PANDAS_SOURCE = pandas-$(PYTHON_PANDAS_VERSION).tar.gz
PYTHON_PANDAS_SITE = https://files.pythonhosted.org/packages/b7/93/b544dd08092b457d88e10fc1e0989d9397fd32ca936fdfcbb2584178dd2b
PYTHON_PANDAS_DEPENDENCIES = host-python-numpy
PYTHON_PANDAS_SETUP_TYPE = setuptools
PYTHON_PANDAS_LICENSE = BSD
PYTHON_PANDAS_LICENSE_FILES = LICENSE

ifneq ($(BR2_PACKAGE_PYTHON_PANDAS_TESTS),y)
define PYTHON_PANDAS_REMOVE_TESTS
   rm -rf $(TARGET_DIR)/usr/lib/python*/site-packages/pandas/tests
endef
PYTHON_PANDAS_POST_INSTALL_TARGET_HOOKS += PYTHON_PANDAS_REMOVE_TESTS
endif

$(eval $(python-package))
