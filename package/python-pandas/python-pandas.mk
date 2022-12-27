################################################################################
#
# python-pandas
#
################################################################################

PYTHON_PANDAS_VERSION = 1.5.2
PYTHON_PANDAS_SOURCE = pandas-$(PYTHON_PANDAS_VERSION).tar.gz
PYTHON_PANDAS_SITE = https://files.pythonhosted.org/packages/4d/07/c4d69e1acb7723ca49d24fc60a89aa07a914dfb8e7a07fdbb9d8646630cd
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
