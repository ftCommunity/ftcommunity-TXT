################################################################################
#
# ti-uim
#
################################################################################

TI_UIM_VERSION = a75f45be2d5c74fc1dd913d08afc30f09a230aa9
TI_UIM_SITE = git://git.ti.com/ti-bt/uim.git
TI_UIM_LICENSE = GPLv2+

define TI_UIM_BUILD_CMDS
	$(MAKE) -C $(@D) $(TARGET_CONFIGURE_OPTS)
endef

define TI_UIM_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/uim \
		$(TARGET_DIR)/usr/sbin/uim
endef

$(eval $(generic-package))
