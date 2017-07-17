################################################################################
#
# libssh2
#
################################################################################

LIBSSH2_VERSION = 1.7.0
LIBSSH2_SITE = http://www.libssh2.org/download
LIBSSH2_LICENSE = BSD
LIBSSH2_LICENSE_FILES = COPYING
LIBSSH2_INSTALL_STAGING = YES
LIBSSH2_CONF_OPTS = --disable-examples-build

# Dependency is either on libgcrypt or openssl, guaranteed in Config.in.
# Favour libgcrypt.
ifeq ($(BR2_PACKAGE_LIBGCRYPT),y)
LIBSSH2_DEPENDENCIES += libgcrypt
LIBSSH2_CONF_OPTS += --with-libgcrypt \
	--with-libgcrypt-prefix=$(STAGING_DIR)/usr \
	--without-openssl
# configure.ac forgets to link to dependent libraries of gcrypt breaking static
# linking
LIBSSH2_CONF_ENV += LIBS="`$(STAGING_DIR)/usr/bin/libgcrypt-config --libs`"
else
LIBSSH2_DEPENDENCIES += openssl
LIBSSH2_CONF_OPTS += --with-openssl \
	--with-libssl-prefix=$(STAGING_DIR)/usr \
	--without-libgcrypt
endif

# Add zlib support if enabled
ifeq ($(BR2_PACKAGE_ZLIB),y)
LIBSSH2_DEPENDENCIES += zlib
LIBSSH2_CONF_OPTS += --with-libz \
	--with-libz-prefix=$(STAGING_DIR)/usr
else
LIBSSH2_CONF_OPTS += --without-libz
endif

$(eval $(autotools-package))
