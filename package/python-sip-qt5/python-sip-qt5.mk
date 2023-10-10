################################################################################
#
# python-SIP-QT5
#
################################################################################

PYTHON_SIP_QT5_VERSION = 12.12.1
PYTHON_SIP_QT5_SITE = https://files.pythonhosted.org/packages/c1/61/4055e7a0f36339964956ff415e36f4abf82561904cc49c021da32949fc55
PYTHON_SIP_QT5_SOURCE = PyQt5_sip-${PYTHON_SIP_QT5_VERSION}.tar.gz
PYTHON_SIP_QT5_LICENSE = MIT
PYTHON_SIP_QT5_LICENSE_FILES = LICENSE
PYTHON_SIP_QT5_SETUP_TYPE = setuptools
PYTHON_SIP_QT5_DEPENDENCIES += python-sip

$(eval $(python-package))
