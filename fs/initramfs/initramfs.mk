################################################################################
#
# Build a kernel with an integrated initial ramdisk filesystem based on cpio.
#
################################################################################

ifeq ($(BR2_TARGET_ROOTFS_INITRAMFS_ROOTFS),y)
ROOTFS_INITRAMFS_DEPENDENCIES += rootfs-cpio
endif

ROOTFS_INITRAMFS_DEPENDENCIES += $(BINARIES_DIR)/initramfs.cpio

# The generic fs infrastructure isn't very useful here.

rootfs-initramfs: $(ROOTFS_INITRAMFS_DEPENDENCIES) linux-rebuild-with-initramfs

rootfs-initramfs-show-depends:
	@echo $(ROOTFS_INITRAMFS_DEPENDENCIES)

.PHONY: rootfs-initramfs rootfs-initramfs-show-depends

ifeq ($(BR2_TARGET_ROOTFS_INITRAMFS_ROOTFS),y)
$(BINARIES_DIR)/initramfs.cpio: rootfs-cpio
	ln -sf rootfs.cpio $(BINARIES_DIR)/initramfs.cpio
endif

ifeq ($(BR2_TARGET_ROOTFS_INITRAMFS_CUSTOM),y)
$(BINARIES_DIR)/initramfs.cpio: target-finalize $(call qstrip,$(BR2_TARGET_ROOTFS_INITRAMFS_CUSTOM_CONTENTS))
	$(LINUX_DIR)/usr/gen_init_cpio $(BR2_TARGET_ROOTFS_INITRAMFS_CUSTOM_CONTENTS) > $(BINARIES_DIR)/initramfs.cpio
endif

ifeq ($(BR2_TARGET_ROOTFS_INITRAMFS),y)
TARGETS_ROOTFS += rootfs-initramfs
endif
