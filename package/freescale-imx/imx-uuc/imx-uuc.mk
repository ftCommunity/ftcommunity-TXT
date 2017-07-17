################################################################################
#
# imx-uuc
#
################################################################################

IMX_UUC_VERSION = 3440b1108373e79669cc17ba1d2be91a123a2053
IMX_UUC_SITE = $(call github,NXPmicro,imx-uuc,$(IMX_UUC_VERSION))
IMX_UUC_LICENSE = GPLv2+
IMX_UUC_LICENSE_FILES = COPYING

# mkfs.vfat is needed to create a FAT partition used by g_mass_storage
# so Windows do not offer to format the device when connected to the PC.
IMX_UUC_DEPENDENCIES = host-dosfstools

define IMX_UUC_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) CC=$(TARGET_CC)
endef

define IMX_UUC_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 755 $(@D)/uuc $(TARGET_DIR)/usr/bin/uuc
	$(INSTALL) -D -m 755 $(@D)/sdimage $(TARGET_DIR)/usr/bin/sdimage
	dd if=/dev/zero of=$(TARGET_DIR)/fat bs=1M count=1
	$(HOST_DIR)/usr/sbin/mkfs.vfat $(TARGET_DIR)/fat
endef

define IMX_UUC_INSTALL_INIT_SYSV
	$(INSTALL) -D -m 0755 package/freescale-imx/imx-uuc/S80imx-uuc \
		$(TARGET_DIR)/etc/init.d/S80imx-uuc
endef

define IMX_UUC_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 0644 package/freescale-imx/imx-uuc/imx-uuc.service \
		$(TARGET_DIR)/usr/lib/systemd/system/imx-uuc.service
	mkdir -p $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/
	ln -fs ../../../../usr/lib/systemd/system/imx-uuc.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/imx-uuc.service
endef

$(eval $(generic-package))
