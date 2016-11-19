################################################################################
#
# python-ipython_genutils
#
################################################################################

PYTHON_IPYTHON_GENUTILS_VERSION = 0.1.0
PYTHON_IPYTHON_GENUTILS_SOURCE = ipython_genutils-$(PYTHON_IPYTHON_GENUTILS_VERSION).tar.gz
PYTHON_IPYTHON_GENUTILS_SITE = https://pypi.python.org/packages/71/b7/a64c71578521606edbbce15151358598f3dfb72a3431763edc2baf19e71f
PYTHON_IPYTHON_GENUTILS_SETUP_TYPE = distutils
PYTHON_IPYTHON_GENUTILS_LICENSE = BSD

$(eval $(python-package))
