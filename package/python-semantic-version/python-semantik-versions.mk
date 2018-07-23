################################################################################
#
# python-semantic-version
#
################################################################################

PYTHON_SEMANTIC_VERSION_VERSION = 2.6.0
PYTHON_SEMANTIC_VERSION_SOURCE = semantic_version-$(PYTHON_SEMANTIC_VERSION_VERSION).tar.gz
PYTHON_SEMANTIC_VERSION_SITE = https://pypi.python.org/packages/72/83/f76958017f3094b072d8e3a72d25c3ed65f754cc607fdb6a7b33d84ab1d5
PYTHON_SEMANTIC_VERSION_SETUP_TYPE = setuptools
PYTHON_SEMANTIC_VERSION_LICENSE = BSD

$(eval $(python-package))
