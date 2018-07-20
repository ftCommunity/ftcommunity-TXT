#
# Macro that builds the needed Makefile target to create a root
# filesystem image.
#
# The following variable must be defined before calling this macro
#
#  ROOTFS_$(FSTYPE)_CMD, the command that generates the root
#  filesystem image. A single command is allowed. The filename of the
#  filesystem image that it must generate is $$@.
#
# The following variables can optionaly be defined
#
#  ROOTFS_$(FSTYPE)_DEPENDENCIES, the list of dependencies needed to
#  build the root filesystem (usually host tools)
#
#  ROOTFS_$(FSTYPE)_PRE_GEN_HOOKS, a list of hooks to call before
#  generating the filesystem image
#
#  ROOTFS_$(FSTYPE)_POST_GEN_HOOKS, a list of hooks to call after
#  generating the filesystem image
#
# In terms of configuration option, this macro assumes that the
# BR2_TARGET_ROOTFS_$(FSTYPE) config option allows to enable/disable
# the generation of a filesystem image of a particular type. If
# the configuration options BR2_TARGET_ROOTFS_$(FSTYPE)_GZIP,
# BR2_TARGET_ROOTFS_$(FSTYPE)_BZIP2 or
# BR2_TARGET_ROOTFS_$(FSTYPE)_LZMA exist and are enabled, then the
# macro will automatically generate a compressed filesystem image.

FS_DIR = $(BUILD_DIR)/buildroot-fs
FULL_DEVICE_TABLE = $(FS_DIR)/device_table.txt
ROOTFS_DEVICE_TABLES = $(call qstrip,$(BR2_ROOTFS_DEVICE_TABLE) \
	$(BR2_ROOTFS_STATIC_DEVICE_TABLE))
USERS_TABLE = $(FS_DIR)/users_table.txt
ROOTFS_USERS_TABLES = $(call qstrip,$(BR2_ROOTFS_USERS_TABLES))

ifeq ($(BR2_REPRODUCIBLE),y)
define ROOTFS_REPRODUCIBLE
	find $(TARGET_DIR) -print0 | xargs -0 -r touch -hd @$(SOURCE_DATE_EPOCH)
endef
endif

ROOTFS_COMMON_TAR = $(FS_DIR)/rootfs.common.tar

# Command to create the common tarball from the base target directory.
define ROOTFS_COMMON_TAR_CMD
	tar cf $(ROOTFS_COMMON_TAR) --numeric-owner \
		--exclude=$(notdir $(TARGET_DIR_WARNING_FILE)) \
		-C $(TARGET_DIR) .
endef

# Command to extract the common tarball into the per-rootfs target directory
define ROOTFS_COMMON_UNTAR_CMD
	mkdir -p $(TARGET_DIR)
	tar xf $(ROOTFS_COMMON_TAR) -C $(TARGET_DIR)
endef

.PHONY: rootfs-common
rootfs-common: $(ROOTFS_COMMON_TAR)

# Emulate being in a filesystem, so that we can have our own TARGET_DIR.
ROOTFS_COMMON_TARGET_DIR = $(FS_DIR)/target

ROOTFS_COMMON_DEPENDENCIES = \
	host-fakeroot host-makedevs \
	$(if $(PACKAGES_USERS)$(ROOTFS_USERS_TABLES),host-mkpasswd)

$(ROOTFS_COMMON_TAR): ROOTFS=COMMON
$(ROOTFS_COMMON_TAR): FAKEROOT_SCRIPT=$(FS_DIR)/fakeroot.fs
$(ROOTFS_COMMON_TAR): $(ROOTFS_COMMON_DEPENDENCIES) target-finalize
	@$(call MESSAGE,"Generating common rootfs tarball")
	rm -rf $(FS_DIR)
	mkdir -p $(FS_DIR)
	rsync -auH $(BASE_TARGET_DIR)/ $(TARGET_DIR)
	echo '#!/bin/sh' > $(FAKEROOT_SCRIPT)
	echo "set -e" >> $(FAKEROOT_SCRIPT)
	echo "chown -h -R 0:0 $(TARGET_DIR)" >> $(FAKEROOT_SCRIPT)
ifneq ($(ROOTFS_USERS_TABLES),)
	cat $(ROOTFS_USERS_TABLES) >> $(USERS_TABLE)
endif
	$(call PRINTF,$(PACKAGES_USERS)) >> $(USERS_TABLE)
	PATH=$(BR_PATH) $(TOPDIR)/support/scripts/mkusers $(USERS_TABLE) $(TARGET_DIR) >> $(FAKEROOT_SCRIPT)
ifneq ($(ROOTFS_DEVICE_TABLES),)
	cat $(ROOTFS_DEVICE_TABLES) > $(FULL_DEVICE_TABLE)
ifeq ($(BR2_ROOTFS_DEVICE_CREATION_STATIC),y)
	$(call PRINTF,$(PACKAGES_DEVICES_TABLE)) >> $(FULL_DEVICE_TABLE)
endif
endif
	$(call PRINTF,$(PACKAGES_PERMISSIONS_TABLE)) >> $(FULL_DEVICE_TABLE)
	echo "$(HOST_DIR)/bin/makedevs -d $(FULL_DEVICE_TABLE) $(TARGET_DIR)" >> $(FAKEROOT_SCRIPT)
	$(foreach s,$(call qstrip,$(BR2_ROOTFS_POST_FAKEROOT_SCRIPT)),\
		echo "echo '$(TERM_BOLD)>>>   Executing fakeroot script $(s)$(TERM_RESET)'" >> $(FAKEROOT_SCRIPT); \
		echo $(EXTRA_ENV) $(s) $(TARGET_DIR) $(BR2_ROOTFS_POST_SCRIPT_ARGS) >> $(FAKEROOT_SCRIPT)$(sep))
	$(foreach hook,$(ROOTFS_PRE_CMD_HOOKS),\
		$(call PRINTF,$($(hook))) >> $(FAKEROOT_SCRIPT)$(sep))
	$(call PRINTF,$(ROOTFS_COMMON_TAR_CMD)) >> $(FAKEROOT_SCRIPT)
	chmod a+x $(FAKEROOT_SCRIPT)
	PATH=$(BR_PATH) $(HOST_DIR)/bin/fakeroot -- $(FAKEROOT_SCRIPT)
	$(Q)rm -rf $(TARGET_DIR)

rootfs-common-show-depends:
	@echo $(ROOTFS_COMMON_DEPENDENCIES)

# Since this function will be called from within an $(eval ...)
# all variable references except the arguments must be $$-quoted.
define inner-rootfs

ROOTFS_$(2)_DIR = $$(FS_DIR)/$(1)
ROOTFS_$(2)_TARGET_DIR = $$(ROOTFS_$(2)_DIR)/target

ROOTFS_$(2)_DEPENDENCIES += rootfs-common

ifeq ($$(BR2_TARGET_ROOTFS_$(2)_GZIP),y)
ROOTFS_$(2)_COMPRESS_EXT = .gz
ROOTFS_$(2)_COMPRESS_CMD = gzip -9 -c
endif
ifeq ($$(BR2_TARGET_ROOTFS_$(2)_BZIP2),y)
ROOTFS_$(2)_COMPRESS_EXT = .bz2
ROOTFS_$(2)_COMPRESS_CMD = bzip2 -9 -c
endif
ifeq ($$(BR2_TARGET_ROOTFS_$(2)_LZMA),y)
ROOTFS_$(2)_DEPENDENCIES += host-lzma
ROOTFS_$(2)_COMPRESS_EXT = .lzma
ROOTFS_$(2)_COMPRESS_CMD = $$(LZMA) -9 -c
endif
ifeq ($$(BR2_TARGET_ROOTFS_$(2)_LZ4),y)
ROOTFS_$(2)_DEPENDENCIES += host-lz4
ROOTFS_$(2)_COMPRESS_EXT = .lz4
ROOTFS_$(2)_COMPRESS_CMD = lz4 -l -9 -c
endif
ifeq ($$(BR2_TARGET_ROOTFS_$(2)_LZO),y)
ROOTFS_$(2)_DEPENDENCIES += host-lzop
ROOTFS_$(2)_COMPRESS_EXT = .lzo
ROOTFS_$(2)_COMPRESS_CMD = $$(LZOP) -9 -c
endif
ifeq ($$(BR2_TARGET_ROOTFS_$(2)_XZ),y)
ROOTFS_$(2)_DEPENDENCIES += host-xz
ROOTFS_$(2)_COMPRESS_EXT = .xz
ROOTFS_$(2)_COMPRESS_CMD = xz -9 -C crc32 -c
endif

$$(BINARIES_DIR)/rootfs.$(1): ROOTFS=$(2)
$$(BINARIES_DIR)/rootfs.$(1): FAKEROOT_SCRIPT=$$(ROOTFS_$(2)_DIR)/fakeroot
$$(BINARIES_DIR)/rootfs.$(1): $$(ROOTFS_$(2)_DEPENDENCIES)
	@$$(call MESSAGE,"Generating root filesystem image rootfs.$(1)")
	rm -rf $$(ROOTFS_$(2)_DIR)
	mkdir -p $$(ROOTFS_$(2)_DIR)
	echo '#!/bin/sh' > $$(FAKEROOT_SCRIPT)
	echo "set -e" >> $$(FAKEROOT_SCRIPT)
	$$(call PRINTF,$$(ROOTFS_COMMON_UNTAR_CMD)) >> $$(FAKEROOT_SCRIPT)
	$$(foreach hook,$$(ROOTFS_$(2)_PRE_GEN_HOOKS),\
		$$(call PRINTF,$$($$(hook))) >> $$(FAKEROOT_SCRIPT)$$(sep))
	$$(call PRINTF,$$(ROOTFS_REPRODUCIBLE)) >> $$(FAKEROOT_SCRIPT)
	$$(call PRINTF,$$(ROOTFS_$(2)_CMD)) >> $$(FAKEROOT_SCRIPT)
	chmod a+x $$(FAKEROOT_SCRIPT)
	PATH=$$(BR_PATH) $$(HOST_DIR)/bin/fakeroot -- $$(FAKEROOT_SCRIPT)
	$(Q)rm -rf $$(TARGET_DIR)
ifneq ($$(ROOTFS_$(2)_COMPRESS_CMD),)
	PATH=$$(BR_PATH) $$(ROOTFS_$(2)_COMPRESS_CMD) $$@ > $$@$$(ROOTFS_$(2)_COMPRESS_EXT)
endif
	$$(foreach hook,$$(ROOTFS_$(2)_POST_GEN_HOOKS),$$(call $$(hook))$$(sep))

rootfs-$(1)-show-depends:
	@echo $$(ROOTFS_$(2)_DEPENDENCIES)

rootfs-$(1): $$(BINARIES_DIR)/rootfs.$(1)

.PHONY: rootfs-$(1) rootfs-$(1)-show-depends

ifeq ($$(BR2_TARGET_ROOTFS_$(2)),y)
TARGETS_ROOTFS += rootfs-$(1)
PACKAGES += $$(filter-out rootfs-%,$$(ROOTFS_$(2)_DEPENDENCIES))
endif

# Check for legacy POST_TARGETS rules
ifneq ($$(ROOTFS_$(2)_POST_TARGETS),)
$$(error Filesystem $(1) uses post-target rules, which are no longer supported.\
	Update $(1) to use post-gen hooks instead)
endif

endef

# $(pkgname) also works well to return the filesystem name
rootfs = $(call inner-rootfs,$(pkgname),$(call UPPERCASE,$(pkgname)))

include $(sort $(wildcard fs/*/*.mk))
