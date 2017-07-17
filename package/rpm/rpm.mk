################################################################################
#
# rpm
#
################################################################################

RPM_VERSION_MAJOR = 4.13
RPM_VERSION = $(RPM_VERSION_MAJOR).0.1
RPM_SOURCE = rpm-$(RPM_VERSION).tar.bz2
RPM_SITE = http://ftp.rpm.org/releases/rpm-$(RPM_VERSION_MAJOR).x
RPM_DEPENDENCIES = host-pkgconf berkeleydb file popt zlib
RPM_LICENSE = GPLv2 or LGPLv2 (library only)
RPM_LICENSE_FILES = COPYING
RPM_PATCH = \
	https://github.com/rpm-software-management/rpm/commit/b5f1895aae096836d6e8e155ee289e1b10fcabcb.patch \
	https://github.com/rpm-software-management/rpm/commit/c810a0aca3f1148d2072d44b91b8cc9caeb4cf19.patch

# b5f1895aae096836d6e8e155ee289e1b10fcabcb.patch
# c810a0aca3f1148d2072d44b91b8cc9caeb4cf19.patch
RPM_AUTORECONF = YES

RPM_CONF_OPTS = \
	--disable-python \
	--disable-rpath \
	--with-external-db \
	--with-gnu-ld \
	--without-cap \
	--without-hackingdocs \
	--without-lua

ifeq ($(BR2_PACKAGE_ACL),y)
RPM_DEPENDENCIES += acl
RPM_CONF_OPTS += --with-acl
else
RPM_CONF_OPTS += --without-acl
endif

ifeq ($(BR2_PACKAGE_LIBNSS),y)
RPM_DEPENDENCIES += libnss
RPM_CONF_OPTS += --without-beecrypt
RPM_CFLAGS += -I$(STAGING_DIR)/usr/include/nss -I$(STAGING_DIR)/usr/include/nspr
else
RPM_DEPENDENCIES += beecrypt
RPM_CONF_OPTS += --with-beecrypt
RPM_CFLAGS += -I$(STAGING_DIR)/usr/include/beecrypt
endif

ifeq ($(BR2_NEEDS_GETTEXT_IF_LOCALE),y)
RPM_DEPENDENCIES += gettext
RPM_CONF_OPTS += --with-libintl-prefix=$(STAGING_DIR)/usr
else
RPM_CONF_OPTS += --without-libintl-prefix
endif

ifeq ($(BR2_PACKAGE_LIBARCHIVE),y)
RPM_DEPENDENCIES += libarchive
RPM_CONF_OPTS += --with-archive
else
RPM_CONF_OPTS += --without-archive
endif

ifeq ($(BR2_PACKAGE_LIBSELINUX),y)
RPM_DEPENDENCIES += libselinux
RPM_CONF_OPTS += --with-selinux
else
RPM_CONF_OPTS += --without-selinux
endif

# For the elfutils and binutils dependencies, there are no
# configuration options to explicitly enable/disable them.
ifeq ($(BR2_PACKAGE_ELFUTILS),y)
RPM_DEPENDENCIES += elfutils
endif

ifeq ($(BR2_PACKAGE_BINUTILS),y)
RPM_DEPENDENCIES += binutils
endif

# RPM, when using NLS, requires GNU gettext's _nl_msg_cat_cntr, which is not
# provided in musl.
ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
RPM_CONF_OPTS += --disable-nls
endif

# ac_cv_prog_cc_c99: RPM uses non-standard GCC extensions (ex. `asm`).
RPM_CONF_ENV = \
	ac_cv_prog_cc_c99='-std=gnu99' \
	CFLAGS="$(TARGET_CFLAGS) $(RPM_CFLAGS)"

$(eval $(autotools-package))
