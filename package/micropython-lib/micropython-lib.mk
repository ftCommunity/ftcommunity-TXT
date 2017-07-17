################################################################################
#
# micropython-lib
#
################################################################################

MICROPYTHON_LIB_VERSION = v1.8.6
MICROPYTHON_LIB_SITE = $(call github,micropython,micropython-lib,$(MICROPYTHON_LIB_VERSION))
MICROPYTHON_LIB_LICENSE = Python software foundation license v2 (some modules), MIT (everything else)
MICROPYTHON_LIB_LICENSE_FILES = LICENSE

define MICROPYTHON_LIB_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) \
		PREFIX=$(TARGET_DIR)/usr/lib/micropython \
		install
endef

$(eval $(generic-package))
