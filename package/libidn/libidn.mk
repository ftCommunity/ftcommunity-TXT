################################################################################
#
# libidn
#
################################################################################

LIBIDN_VERSION = 1.33
LIBIDN_SITE = $(BR2_GNU_MIRROR)/libidn
LIBIDN_INSTALL_STAGING = YES
LIBIDN_CONF_ENV = EMACS="no" MAKEINFO=true
LIBIDN_CONF_OPTS = --disable-java --enable-csharp=no
LIBIDN_DEPENDENCIES = host-pkgconf $(if $(BR2_NEEDS_GETTEXT_IF_LOCALE),gettext) $(if $(BR2_PACKAGE_LIBICONV),libiconv)
LIBIDN_LICENSE = GPLv2+, GPLv3+, LGPLv3+
LIBIDN_LICENSE_FILES = COPYINGv2 COPYINGv3 COPYING.LESSERv3
# lib/punycode.c patch triggers reconf in doc/
LIBIDN_AUTORECONF = YES

define LIBIDN_REMOVE_BINARY
	rm -f $(TARGET_DIR)/usr/bin/idn
endef

ifneq ($(BR2_PACKAGE_LIBIDN_BINARY),y)
LIBIDN_POST_INSTALL_TARGET_HOOKS += LIBIDN_REMOVE_BINARY
endif

define LIBIDN_REMOVE_EMACS_STUFF
	rm -rf $(TARGET_DIR)/usr/share/emacs
endef

LIBIDN_POST_INSTALL_TARGET_HOOKS += LIBIDN_REMOVE_EMACS_STUFF

$(eval $(autotools-package))
