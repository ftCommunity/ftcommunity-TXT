################################################################################
#
# python-traitlets
#
################################################################################

PYTHON_TRAITLETS_VERSION = 4.3.1
PYTHON_TRAITLETS_SOURCE = traitlets-$(PYTHON_TRAITLETS_VERSION).tar.gz
PYTHON_TRAITLETS_SITE = https://pypi.python.org/packages/b1/d6/5b5aa6d5c474691909b91493da1e8972e309c9f01ecfe4aeafd272eb3234
PYTHON_TRAITLETS_SETUP_TYPE = distutils
PYTHON_TRAITLETS_LICENSE = BSD

$(eval $(python-package))
