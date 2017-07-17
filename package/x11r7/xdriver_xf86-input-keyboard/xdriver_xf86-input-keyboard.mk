################################################################################
#
# xdriver_xf86-input-keyboard
#
################################################################################

XDRIVER_XF86_INPUT_KEYBOARD_VERSION = 1.9.0
XDRIVER_XF86_INPUT_KEYBOARD_SOURCE = xf86-input-keyboard-$(XDRIVER_XF86_INPUT_KEYBOARD_VERSION).tar.bz2
XDRIVER_XF86_INPUT_KEYBOARD_SITE = http://xorg.freedesktop.org/releases/individual/driver
XDRIVER_XF86_INPUT_KEYBOARD_LICENSE = MIT
XDRIVER_XF86_INPUT_KEYBOARD_LICENSE_FILES = COPYING
XDRIVER_XF86_INPUT_KEYBOARD_DEPENDENCIES = xserver_xorg-server xproto_inputproto xproto_kbproto xproto_randrproto xproto_xproto
XDRIVER_XF86_INPUT_KEYBOARD_CONF_OPTS = --disable-selective-werror

$(eval $(autotools-package))
