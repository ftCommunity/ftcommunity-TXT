################################################################################
#
# sngrep
#
################################################################################

SNGREP_VERSION = v1.4.2
SNGREP_SITE = $(call github,irontec,sngrep,$(SNGREP_VERSION))
SNGREP_LICENSE = GPLv3+
SNGREP_LICENSE_FILES = LICENSE
SNGREP_AUTORECONF = YES
SNGREP_DEPENDENCIES = libpcap ncurses host-pkgconf

SNGREP_CONF_ENV += \
	$(if $(BR2_STATIC_LIBS),LIBS="`$(STAGING_DIR)/usr/bin/pcap-config --static --libs`")

# our ncurses wchar support is not properly detected
SNGREP_CONF_OPTS += --disable-unicode

# openssl and gnutls can't be enabled at the same time.
ifeq ($(BR2_PACKAGE_OPENSSL),y)
SNGREP_DEPENDENCIES += openssl
SNGREP_CONF_OPTS += --with-openssl --without-gnutls
# gnutls support also requires libgcrypt
else ifeq ($(BR2_PACKAGE_GNUTLS)$(BR2_PACKAGE_LIBGCRYPT),yy)
SNGREP_DEPENDENCIES += gnutls
SNGREP_CONF_OPTS += --with-gnutls --without-openssl
else
SNGREP_CONF_OPTS += --without-gnutls --without-openssl
endif

ifeq ($(BR2_PACKAGE_PCRE),y)
SNGREP_DEPENDENCIES += pcre
SNGREP_CONF_OPTS += --with-pcre
else
SNGREP_CONF_OPTS += --without-pcre
endif

$(eval $(autotools-package))
