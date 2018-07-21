################################################################################
#
# libupnp18
#
################################################################################

LIBUPNP18_VERSION = 1.8.3
LIBUPNP18_SOURCE = libupnp-$(LIBUPNP18_VERSION).tar.bz2
LIBUPNP18_SITE = http://downloads.sourceforge.net/project/pupnp/pupnp/libUPnP%20$(LIBUPNP18_VERSION)
LIBUPNP18_CONF_ENV = ac_cv_lib_compat_ftime=no
LIBUPNP18_INSTALL_STAGING = YES
LIBUPNP18_LICENSE = BSD-3-Clause
LIBUPNP18_LICENSE_FILES = LICENSE

ifeq ($(BR2_PACKAGE_OPENSSL),y)
LIBUPNP18_CONF_OPTS += --enable-open-ssl
LIBUPNP18_DEPENDENCIES += host-pkgconf openssl
LIBUPNP18_CONF_ENV += LIBS="`$(PKG_CONFIG_HOST_BINARY) --libs libssl libcrypto`"
else
LIBUPNP18_CONF_OPTS += --disable-open-ssl
endif

$(eval $(autotools-package))
