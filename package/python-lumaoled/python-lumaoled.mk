################################################################################
#
# python-lumaoled
#
################################################################################

PYTHON_LUMAOLED_VERSION = 3.1.0
PYTHON_LUMAOLED_SOURCE = luma.oled-$(PYTHON_LUMAOLED_VERSION).tar.gz
PYTHON_LUMAOLED_SITE = https://files.pythonhosted.org/packages/36/08/7ac66533b6561c7fd27ded6896960f77b459334a124149005efefc05d4e5
PYTHON_LUMAOLED_SETUP_TYPE = setuptools
PYTHON_LUMAOLED_LICENSE = MIT
PYTHON_LUMAOLED_LICENSE_FILES = LICENSE.rst

$(eval $(python-package))
