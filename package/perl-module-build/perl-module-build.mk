################################################################################
#
# perl-module-build
#
################################################################################

PERL_MODULE_BUILD_VERSION = 0.4220
PERL_MODULE_BUILD_SOURCE = Module-Build-$(PERL_MODULE_BUILD_VERSION).tar.gz
PERL_MODULE_BUILD_SITE = $(BR2_CPAN_MIRROR)/authors/id/L/LE/LEONT
PERL_MODULE_BUILD_LICENSE = Artistic or GPLv1+
PERL_MODULE_BUILD_LICENSE_FILES = LICENSE

$(eval $(host-perl-package))
