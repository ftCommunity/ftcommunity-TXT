# XZCAT is taken from BR2_XZCAT (defaults to 'xzcat') (see Makefile)
# If it is not present, build our own host-xzcat

ifeq (,$(call suitable-host-package,xzcat,$(XZCAT)))
DEPENDENCIES_HOST_PREREQ += host-xz
EXTRACTOR_DEPENDENCY_PRECHECKED_EXTENSIONS += .xz .lzma
XZCAT = $(HOST_DIR)/usr/bin/xzcat
endif
