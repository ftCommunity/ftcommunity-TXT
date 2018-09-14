
all: buildroot/Makefile buildroot/.config
	make -C buildroot

buildroot/Makefile:
	git submodule update --init buildroot

buildroot/.config:
	BR2_EXTERNAL=.. make -C buildroot fischertechnik_TXT_defconfig

imagedir := buildroot/output/images

release: all
	$(eval version := $(shell cat buildroot/output/target/etc/fw-ver.txt))
	$(eval zipfile := build/ftcommunity-txt-$(version).zip)
	mkdir -p $(zipdir)
	rm -f $(zipfile)
	zip -j $(zipfile) $(imagedir)/am335x-kno_txt.dtb $(imagedir)/rootfs.img $(imagedir)/uImage
