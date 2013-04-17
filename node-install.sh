#!/bin/bash

set -o nounset
set -o errexit

SCRIPT_NAME=`basename $0`
pushd `dirname $0` > /dev/null
SCRIPT_PATH=`pwd`
popd > /dev/null
CONFIG_SCRIPT=config.sh

NODE_NUMBER=0
MIN_NODE=1
MAX_NODE=199


. ${SCRIPT_PATH}/${CONFIG_SCRIPT}

prepare_hdd() {
    # check ${INSTALL_HDD} is not Live media (or already mounted)
    if mount | grep ${INSTALL_HDD}; then
        echo "${INSTALL_HDD} appears to already be mounted - bailing"
        exit 1
    fi

    modprobe dm-mod     # probably already loaded, but doesn't hurt

    sgdisk --clear --mbrtogpt ${INSTALL_HDD}
    sgdisk --new 1:0:+100M \
           --typecode 1:8300 \
           --change-name 1:"Boot Partition" ${INSTALL_HDD}
    sgdisk --new 2:0:0 \
           --typecode 2:8300 \
           --change-name 2:"Root Partition" ${INSTALL_HDD}
    sgdisk --attributes=1:set:2 ${INSTALL_HDD}
    # Format disk
    mkfs.ext4 -L boot ${BOOT_PART}
    mkfs.ext4 -L root ${ROOT_PART}
}


mount_partitions() {
    mount ${ROOT_PART} /mnt
    mkdir -p /mnt/boot
    mount ${BOOT_PART} /mnt/boot
    fallocate -l ${SWAP_SIZE} /mnt${SWAP_FILE}
    chmod 600 /mnt${SWAP_FILE}
    mkswap /mnt${SWAP_FILE}
    swapon /mnt${SWAP_FILE}
}

unmount_partitions() {
    umount /mnt/boot
    swapoff /mnt${SWAP_FILE}
    umount /mnt
}


bootstrap_system() {
    # copy premade config files to /mnt
    cp mntfiles/etc/pacman.conf /etc/pacman.conf
    pacstrap /mnt base base-devel
    rsync -avz mntfiles/ /mnt/

    # generate fstab
    genfstab -U -p /mnt >> /mnt/etc/fstab
}



live_install_main() {
    prepare_hdd
    mount_partitions
    bootstrap_system

    cp ${SCRIPT_PATH}/${SCRIPT_NAME} /mnt/root/${SCRIPT_NAME}
    cp ${SCRIPT_PATH}/${CONFIG_SCRIPT} /mnt/root/${CONFIG_SCRIPT}

    # call this same script except now use 'chrootstage'
    arch-chroot /mnt /root/${SCRIPT_NAME} ${NODE_NUMBER} in-chroot 

    rm /mnt/root/${SCRIPT_NAME}
    rm /mnt/root/${CONFIG_SCRIPT}

    unmount_partitions
}



chroot_stage_main() {
    NODE_IP=${BASE_IP}.${NODE_NUMBER}
    HOSTNAME=${BASE_NAME}${NODE_NUMBER}

    locale-gen
    ln -s /usr/share/zoneinfo/${ZONE_INFO} /etc/localtime
    hwclock --systohc --utc
    echo ${HOSTNAME} > /etc/hostname

    # rebuild initial ramdisk to include lvm
    mkinitcpio -p linux

    # initialize initial root password
    echo "root:root" | chpasswd

    # setup syslinux
    pacman -Syy
    pacman --noconfirm -S syslinux
    mv /boot/syslinux/syslinux.cfg.REPLACE /boot/syslinux/syslinux.cfg
    dd bs=440 conv=notrunc count=1 if=/usr/lib/syslinux/gptmbr.bin \
       of=/dev/sda
    syslinux-install_update -i

    # setup networking
    pacman --noconfirm -S openssh
    mkdir -p /etc/conf.d
    cat > /etc/conf.d/network << EOF
interface=eth0
address=${NODE_IP}
netmask=${NETMASK}
broadcast=${BROADCAST}
gateway=${MASTER_IP}
EOF

    cat > /etc/resolv.conf << EOF
domain ${DOMAIN}
nameserver ${MASTER_IP}
EOF

    # setup sudo
    chown root:root /etc/sudoers.REPLACE
    mv /etc/sudoers.REPLACE /etc/sudoers

    # install other basic _necessities_
    # zsh -- Who uses bash still?
    # rsync -- better copy
    # salt -- saltstack will do the rest
    pacman --noconfirm -S zsh rsync python python2 wget nfs-utils
    # salt will have to be installed via AUR until it is moved to community
    # We could also keep a local repository database...
    _install_salt

    # enable systemd services (has return code of 1 so disable errexit)
    set +o errexit
    systemctl enable network.service
    systemctl enable sshd.service
    systemctl enable salt-minion.service
    set -o errexit
}

function _install_salt() {
    wget https://aur.archlinux.org/packages/sa/salt/salt.tar.gz
    # Because it won't otherwise be downloaded and installed for us
    wget https://aur.archlinux.org/packages/py/python2-msgpack/python2-msgpack.tar.gz
    tar -zxf python2-msgpack.tar.gz
    cd python2-msgpack
    makepkg --noconfirm --asroot --syncdeps --install
    cd ../
    tar -zxf salt.tar.gz
    cd salt
    makepkg --noconfirm --asroot --syncdeps --install
    cd ../
    mv /etc/salt/minion.REPLACE /etc/salt/minion
    # Cleanup
    rm -r salt salt.tar.gz python2-msgpack python2-msgpack.tar.gz
}

##################################################
# main program entry logic
##################################################

ACTION=full_install

# parse arguments
declare -a args
while (( $# )); do
    case "$1" in
        #-q|--quiet) QUIET=1;;
        in-chroot)
            ACTION=in-chroot;;
        partition)
            ACTION=partition;;
        mount)
            ACTION=mount;;
        umount)
            ACTION=umount;;
        bootstrap)
            ACTION=bootstrap;;
        *)
            args+=("$1")
            ;;
    esac
    shift
done

# test for minimum number of arguments
if [[ -z ${args[0]-} ]]; then
    echo "TODO: make a better usage error message"
    exit 1
fi


NODE_NUMBER=${args[0]}
if [ $NODE_NUMBER -lt $MIN_NODE ] || [ $NODE_NUMBER -gt $MAX_NODE ]; then
    echo "node# must be integer between ${MIN_NODE} and ${MAX_NODE}"
    exit 1
fi


case "$ACTION" in
    full_install)
        live_install_main;;
    in-chroot)
        chroot_stage_main;;
    mount)
        mount_partitions;;
    umount)
        unmount_partitions;;
    bootstrap)
        bootstrap_system;;
    *)
        exit 1;;
esac
