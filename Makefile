ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
OUTPUT_DIR := $(ROOT_DIR)/output
BUILD_DIR := $(OUTPUT_DIR)/build
IMAGE_DIR := $(OUTPUT_DIR)/images
INITRAMFS_DIR := $(OUTPUT_DIR)/initramfs

BR_INIT_ENV := BR2_EXTERNAL=$(ROOT_DIR)


.PHONY: all
all: $(IMAGE_DIR)/rootfs.img

.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)

.PHONY: prepare-structure
prepare-structure:
	mkdir -p $(OUTPUT_DIR)
	mkdir -p $(IMAGE_DIR)
	mkdir -p $(INITRAMFS_DIR)

.PHONY: prepare
prepare: prepare-structure $(BUILD_DIR)/rootfs/.config $(BUILD_DIR)/initramfs/.config

.PHONY: source
source: rootfs-source initramfs-source

.PHONY: rootfs-source
rootfs-source: $(BUILD_DIR)/rootfs/.config
	$(MAKE) -C $(BUILD_DIR)/rootfs source

.PHONY: initramfs-source
initramfs-source: $(BUILD_DIR)/initramfs/.config
	$(MAKE) -C $(BUILD_DIR)/initramfs source

$(BUILD_DIR)/rootfs/.config: $(ROOT_DIR)/buildroot/Makefile
	$(BR_INIT_ENV) $(MAKE) O=$(BUILD_DIR)/rootfs -C $(ROOT_DIR)/buildroot fischertechnik_TXT_rootfs_defconfig

$(BUILD_DIR)/initramfs/.config: $(ROOT_DIR)/buildroot/Makefile
	$(BR_INIT_ENV) $(MAKE) O=$(BUILD_DIR)/initramfs -C $(ROOT_DIR)/buildroot fischertechnik_TXT_initramfs_defconfig

$(ROOT_DIR)/buildroot/Makefile:
	git submodule update --init buildroot

$(IMAGE_DIR)/rootfs.img: $(INITRAMFS_DIR)/initramfs.cpio prepare-structure
	$(MAKE) -C $(BUILD_DIR)/rootfs
	cp $(BUILD_DIR)/rootfs/images/rootfs.squashfs $(IMAGE_DIR)/rootfs.img
	cp $(BUILD_DIR)/rootfs/images/uImage $(IMAGE_DIR)/uImage

$(INITRAMFS_DIR)/initramfs.cpio: $(BUILD_DIR)/initramfs/.config prepare-structure
	$(MAKE) -C $(BUILD_DIR)/initramfs
	cp $(BUILD_DIR)/initramfs/images/rootfs.cpio $(INITRAMFS_DIR)/initramfs.cpio

release: all
	$(eval version := $(shell cat $(BUILD_DIR)/rootfs/target/etc/fw-ver.txt))
	$(eval zipfile := $(IMAGE_DIR)/ftcommunity-txt-$(version).zip)
	rm -f $(zipfile)
	zip -j $(zipfile) $(IMAGE_DIR)/am335x-kno_txt.dtb $(IMAGE_DIR)/rootfs.img $(IMAGE_DIR)/uImage
