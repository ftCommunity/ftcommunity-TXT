################################################################################
#
# python-prompt_toolkit
#
################################################################################

PYTHON_PROMPT_TOOLKIT_VERSION = 1.0.9
PYTHON_PROMPT_TOOLKIT_SOURCE = prompt_toolkit-$(PYTHON_PROMPT_TOOLKIT_VERSION).tar.gz
PYTHON_PROMPT_TOOLKIT_SITE = https://pypi.python.org/packages/83/14/5ac258da6c530eca02852ee25c7a9ff3ca78287bb4c198d0d0055845d856
PYTHON_PROMPT_TOOLKIT_SETUP_TYPE = setuptools
PYTHON_PROMPT_TOOLKIT_LICENSE = BSD-3c
PYTHON_PROMPT_TOOLKIT_LICENSE_FILES = LICENSE

$(eval $(python-package))
