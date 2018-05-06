#!/bin/bash
##
# ubuntu 16.04
# --graphics none 
#
virt-install \
--connect qemu:///system \
--name test.template \
--ram 512 \
--disk pool=default,size=5,bus=virtio,sparse=false \
--network network=default,model=virtio \
--location http://archive.ubuntu.com/ubuntu/dists/xenial/main/installer-amd64 \
--initrd-inject=/var/lib/libvirt/images/preseed.cfg \
--extra-args="locale=en_GB.UTF-8 console-setup/ask_detect=false keyboard-configuration/layoutcode=hu file=file:/preseed.cfg vga=788 quiet" \
--os-type=linux \
--os-variant=ubuntu16.04 \
--video=vga \
--noreboot
exit 0

# Ubuntu 14.04
virt-install \
--connect qemu:///system \
--name test.template \
--ram 512 \
--disk pool=default,size=5,bus=virtio,sparse=false \
--network network=default,model=virtio \
--location http://archive.ubuntu.com/ubuntu/dists/xenial/main/installer-amd64 \
--initrd-inject=/var/lib/libvirt/images/preseed.cfg \
--extra-args="locale=en_GB.UTF-8 console-setup/ask_detect=false keyboard-configuration/layoutcode=hu file=file:/preseed.cfg vga=788 quiet" \
--os-type=linux \
--os-variant=ubuntu16.04 \
--video=vga \
--noreboot
#--virt-type kvm \
