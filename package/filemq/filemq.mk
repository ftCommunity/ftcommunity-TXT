################################################################################
#
# filemq
#
################################################################################

FILEMQ_VERSION = e59951489045825d6fc5bdc6a5a5ecf1abf51943
FILEMQ_SITE = $(call github,zeromq,filemq,$(FILEMQ_VERSION))

FILEMQ_AUTORECONF = YES
FILEMQ_CONF_ENV = filemq_have_asciidoc=no
FILEMQ_INSTALL_STAGING = YES
FILEMQ_DEPENDENCIES = czmq openssl zeromq
FILEMQ_LICENSE = MPLv2.0
FILEMQ_LICENSE_FILES = LICENSE

define FILEMQ_CREATE_CONFIG_DIR
	mkdir -p $(@D)/config
endef

FILEMQ_POST_PATCH_HOOKS += FILEMQ_CREATE_CONFIG_DIR

$(eval $(autotools-package))
