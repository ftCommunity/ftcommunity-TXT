ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
OUTPUT_DIR := $(ROOT_DIR)/output
BUILD_DIR := $(OUTPUT_DIR)/build
IMAGE_DIR := $(OUTPUT_DIR)/images
INITRAMFS_DIR := $(OUTPUT_DIR)/initramfs
BR_INIT_ENV := BR2_EXTERNAL=$(ROOT_DIR)

.PHONY: all
all: rootfs

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)

.PHONY: cleanall
cleanall:
	rm -rf $(OUTPUT_DIR)

.PHONY: config
config: $(BUILD_DIR)/rootfs/.config $(BUILD_DIR)/initramfs/.config

.PHONY: source
source: rootfs-source initramfs-source

.PHONY: rootfs-source
rootfs-source: $(BUILD_DIR)/rootfs/.config
	$(MAKE) -C $(BUILD_DIR)/rootfs source

.PHONY: initramfs-source
initramfs-source: $(BUILD_DIR)/initramfs/.config
	$(MAKE) -C $(BUILD_DIR)/initramfs source

$(BUILD_DIR)/rootfs/.config: $(ROOT_DIR)/buildroot/Makefile configs/fischertechnik_TXT_rootfs_defconfig
	mkdir -p $(BUILD_DIR)/rootfs
	$(BR_INIT_ENV) $(MAKE) O=$(BUILD_DIR)/rootfs -C $(ROOT_DIR)/buildroot fischertechnik_TXT_rootfs_defconfig

$(BUILD_DIR)/initramfs/.config: $(ROOT_DIR)/buildroot/Makefile configs/fischertechnik_TXT_initramfs_defconfig
	mkdir -p $(BUILD_DIR)/initramfs
	$(BR_INIT_ENV) $(MAKE) O=$(BUILD_DIR)/initramfs -C $(ROOT_DIR)/buildroot fischertechnik_TXT_initramfs_defconfig

$(ROOT_DIR)/buildroot/Makefile:
	git submodule update --init buildroot

.PHONY: rootfs
rootfs: $(BUILD_DIR)/rootfs/.config $(INITRAMFS_DIR)/initramfs.cpio
	$(MAKE) -C $(BUILD_DIR)/rootfs
	mkdir -p $(IMAGE_DIR)
	cp $(BUILD_DIR)/rootfs/images/rootfs.squashfs $(IMAGE_DIR)/rootfs.img
	cp $(BUILD_DIR)/rootfs/images/uImage $(IMAGE_DIR)/uImage
	cp $(BUILD_DIR)/rootfs/images/device_tree.dtb $(IMAGE_DIR)/am335x-kno_txt.dtb

.PHONY: initramfs
initramfs: $(BUILD_DIR)/initramfs/.config
	$(MAKE) -C $(BUILD_DIR)/initramfs

.PHONY: copy-initramfs
$(INITRAMFS_DIR)/initramfs.cpio copy-iniramfs: initramfs
	mkdir -p $(INITRAMFS_DIR)
	cp $(BUILD_DIR)/initramfs/images/rootfs.cpio $(INITRAMFS_DIR)/initramfs.cpio

release: rootfs initramfs
	$(eval version := $(shell cat $(BUILD_DIR)/rootfs/target/etc/fw-ver.txt))
	$(eval zipfile := $(IMAGE_DIR)/ftcommunity-txt-$(version).zip)
	rm -f $(zipfile)
	zip -j $(zipfile) $(IMAGE_DIR)/am335x-kno_txt.dtb $(IMAGE_DIR)/rootfs.img $(IMAGE_DIR)/uImage
