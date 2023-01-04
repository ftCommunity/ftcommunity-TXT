
all: buildroot/Makefile buildroot/.config
	make -C buildroot

clean:
	BR2_EXTERNAL=.. make -C buildroot clean

buildroot/Makefile:
	git submodule update --init buildroot

CONFIG_DEPENDS = \
  .gitmodules \
  board/fischertechnik/TXT/tisdk_am335x-fischertechnik_txt_defconfig

buildroot/.config: $(CONFIG_DEPENDS) buildroot/Makefile
	BR2_EXTERNAL=.. make -C buildroot fischertechnik_TXT_defconfig

imagedir := buildroot/output/images

release: all
	$(eval version := $(shell cat buildroot/output/target/etc/fw-ver.txt))
	$(eval zipfile := build/ftcommunity-txt-$(version).zip)
	mkdir -p build
	rm -f $(zipfile)
	zip -j $(zipfile) $(imagedir)/am335x-kno_txt.dtb $(imagedir)/rootfs.img $(imagedir)/uImage
