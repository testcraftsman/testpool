sshpass -p password virsh -c qemu+ssh://mhamilton@192.168.0.27/system list

# clone
virt-clone --connect qemu+ssh://mhamilton@192.168.0.27/system --original template --name vm2 --file /var/lib/libvirt/images/vm2.img
