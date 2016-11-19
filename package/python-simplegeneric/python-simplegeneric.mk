################################################################################
#
# python-simplegeneric
#
################################################################################

PYTHON_SIMPLEGENERIC_VERSION = 0.8.1
PYTHON_SIMPLEGENERIC_SOURCE = simplegeneric-$(PYTHON_SIMPLEGENERIC_VERSION).zip
PYTHON_SIMPLEGENERIC_SITE = https://pypi.python.org/packages/3d/57/4d9c9e3ae9a255cd4e1106bb57e24056d3d0709fc01b2e3e345898e49d5b
PYTHON_SIMPLEGENERIC_SETUP_TYPE = setuptools
PYTHON_SIMPLEGENERIC_LICENSE = ZPL

define PYTHON_SIMPLEGENERIC_EXTRACT_CMDS
	$(UNZIP) -d $(BUILD_DIR) $(DL_DIR)/$(PYTHON_SIMPLEGENERIC_SOURCE)
	mv $(BUILD_DIR)/simplegeneric-$(PYTHON_SIMPLEGENERIC_VERSION)/* $(@D)
	rmdir $(BUILD_DIR)/simplegeneric-$(PYTHON_SIMPLEGENERIC_VERSION)/
endef

$(eval $(python-package))
