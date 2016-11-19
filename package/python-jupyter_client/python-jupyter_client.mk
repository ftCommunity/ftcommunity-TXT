################################################################################
#
# python-jupyter_client
#
################################################################################

PYTHON_JUPYTER_CLIENT_VERSION = 4.4.0
PYTHON_JUPYTER_CLIENT_SOURCE = jupyter_client-$(PYTHON_JUPYTER_CLIENT_VERSION).tar.gz
PYTHON_JUPYTER_CLIENT_SITE = https://pypi.python.org/packages/88/03/d8e218721af0b084d4fda5e3bb89dc201505780f96ae060bf5e3e67c7707
PYTHON_JUPYTER_CLIENT_SETUP_TYPE = distutils
PYTHON_JUPYTER_CLIENT_LICENSE = BSD

$(eval $(python-package))
