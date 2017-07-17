################################################################################
#
# xlib_libXpm
#
################################################################################

XLIB_LIBXPM_VERSION = 3.5.12
XLIB_LIBXPM_SOURCE = libXpm-$(XLIB_LIBXPM_VERSION).tar.bz2
XLIB_LIBXPM_SITE = http://xorg.freedesktop.org/releases/individual/lib
XLIB_LIBXPM_LICENSE = MIT
XLIB_LIBXPM_LICENSE_FILES = COPYING
XLIB_LIBXPM_INSTALL_STAGING = YES
# we patch configure.ac
XLIB_LIBXPM_AUTORECONF = YES
XLIB_LIBXPM_DEPENDENCIES = xlib_libX11 xlib_libXext xlib_libXt xproto_xproto \
	$(if $(BR2_PACKAGE_GETTEXT),gettext) \
	$(if $(BR2_PACKAGE_LIBICONV),libiconv) \
	host-gettext

$(eval $(autotools-package))
