################################################################################
#
# python-ipython
#
################################################################################

PYTHON_IPYTHON_VERSION = 5.1.0
PYTHON_IPYTHON_SOURCE = ipython-$(PYTHON_IPYTHON_VERSION).tar.gz
PYTHON_IPYTHON_SITE = https://pypi.python.org/packages/89/63/a9292f7cd9d0090a0f995e1167f3f17d5889dcbc9a175261719c513b9848
PYTHON_IPYTHON_SETUP_TYPE = distutils
PYTHON_IPYTHON_LICENSE = BSD

$(eval $(python-package))
