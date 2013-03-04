#!/usr/bin/env python

import os
import configparser
import subprocess
import sys
import logging

logger = logging.GetLogger("install")
logger.addHandler(logging.StreamHandler())

def getConfig(section, key):
    config = configpaser.ConfigParser()
    config.read("install.config")
    return config[section][key]

def getKeys(section):
    config = configparser.ConfigParser()
    config.read("install.config")
    return config[section]

def call(cmd, input=None, stdout=None, stderr=None, noop=True, verbose=False):
    if noop or verbose:
        logger.debug(cmd)
        if input:
            logger.debug(input)
    if not noop:
        p = subproccess.Popen(cmd, stdout=stdout, stderr=stderr,
                              stdin=subprocess.PIPE if input else None)
        p.communicat(input=input)

def prepare_disks():
    ROOT = getConfig("DISK_INFO", "ROOT")
    DEVICES = getKeys("PARTITION_TABLE")
    for device in DEVICES:
        partitionDisk(device)

def partitionDisk(device):
    logger.INFO("Partitioning %s" % device)
    partitionTable = getConfig("PARTITION_TABLE", device)
    partitions = partitionTable.split('|')
    logger.debug("Erasing current partition table")
    dd_cmd = ["dd", "if=/dev/zero", "of=%s" %device, "bs=512", "cound=1"]
    call(dd_cmd)
    logger.debug("Initializing new disk label")
    mklabel_cmd = ["parted", device, "mklabel", "gpt"]
    call(mklabel_cmd)
    for i, part in enumerate(partitions):
        logger.debug("Creating %d partition" % i)
        options = part.split(";")
        assert 3 <= len(options) <= 3 ##this may later grow
        parted_cmd = ["parted",
                      device,
                      "mkpart",
                      "P1",
                      options[2],
                      options[1],
                      options[2]]
        call(parted_cmd)
        if option[2] not in ["ext2","ext3","ext4"]:
            continue
        logger.debug("Making FileSystem")
        mkfs_cmd = ["mkfs.%s" % option[2], device]
        call(mkfs_cmd)

def mount_partitions():
    mounts = getKeys("FSTAB")
    rel_root = "/mnt"
    for mount in mounts:
        logger.debug("(Creating and) mounting %s" % mount)
        dev = getConfig("PARTITION_TABLE", mount)
        m = getConfig("FSTAB", mount)
        mkdir_cmd = ["mkdir", "-p", rel_root + m]
        mount_cmd = ["mount", dev, rel_root + m]
        call(mkdir_cmd)
        call(mount_cmd)

def umount_partitions():
    mounts = getKeys("FSTAB")
    mounts.reverse()
    rel_root = "/mnt"
    for mount in mounts:
        logger.debug("Unmount %s" % mount)
        m = getConfig("FSTAB", mount)
        umount_cmd = ["umount", m]
        call(umount_cmd)

def bootstrap_system():
    pacstrap_cmd = ["pacstrap", "/mnt", "base", "base-devel"]
    call(pacstrap_cmd)
    rsync_cmd = ["rsync", "-avz", "mntfiles", "/mnt/"]
    call(rsync_cmd)
    genfstab_cmd = ["genfstab", "-U", "-p", "/mnt"]
    with open("/mnt/etc/fstab", "a") as fstab:
        call(genfstab, stdout=fstab)

def live_install_main():
    prepare_disks()
    mount_partitions()
    bootstrap_system()
    logger.debug("Copy and call self from chroot")
    copy_self_cmd = ["cp", os.path.join(os.getcwd(), "node-install.py"),
                     "/mnt/root/node-enstall.py"]
    call(copy_self_cmd)
    chroot_cmd = ["arch-chroot",
                  "/mnt",
                  "python",
                  "node-install.py",
                  "node-number",
                  "in-chroot"]
    call(chroot_cmd)
    call(["rm", "/mnt/root/node-install.py"])

    umount_partitions()

def chroot_stage_main():
    hostname = getConfig("HOST", "NAME")
    zoneInfo = getConfig("HOST", "ZONEINFO")
    domain = getConfig("NETWORK", "DOMAIN")
    master_node = getConfig("NETWORK", "MASTER_HOSTNAME")
    master_ip = getConfig("NETWORK", "MASTER_IP")
    netmask = getConfig("NETWORK", "NETMASK")
    broadcast = getConfig("NETWORK", "BROADCAST")
    ip = getConfig("NETWORK", "IP")

    extra_install_cmd = ["pacman",
                         "--noconfirm",
                         "-S",
                         "syslinux",
                         "iproute2",
                         "openssh",
                         "nfs-utils",
                         "nfsidmap",
                         "ntp",
                         "sudo",
                         "zsh",
                         "rsync"]
    call(extra_install_cmd)
    localegen_cmd = ["locale-gen"]
    call(localegen_cmd)

    localtime_cmd = ["ln", "-s",
                     "/usr/share/zoneinfo/%s" % zoneInfo,
                     "/etc/localtime"]
    call(localtime_cmd)

    hwclock_cmd = ["hwclock", "--systohc", "--utc"]
    call(hwclock_cmd)

    hostname_cmd = ["echo", hostname]
    logger.debug("%s piped to /etc/hostname" % hostname_cmd)
    with open("/etc/hostname", "w") as f:
        call(hostname_cmd, stdout=f)

    mkinitcpio_cmd = ["mkinitcpio", "-p", "linux"]
    call(mkinitcpio_cmd)

    call(["chpasswd"], input="root:toor")

    call(["mv", "/boot/syslinux/syslinux.cfg.REPLACE",
          "/boot/syslinux/syslinux.cfg"])

    syslinux_conf_cmd = ["syslinux-install_update", "-iam"]
    call(syslinux_conf_cmd)

    os.path.mkdir("/etc/conf.d")
    with open("/etc/conf.d/network", "w") as f:
        f.write("""
        interface=eth0
        address=%s
        netmask=%s
        broadcast=%s
        gateway=%s""" % (ip, netmask, broadcast, master_ip))
    with open("/etc/resolve.conf", "w") as f:
        f.write("""
        domain %s
        nameserver %s""" % (domain, master_ip))


    ## setup NFS Home...

    chown_cmd = ["chown", "root:root", "/etc/sudoers.REPLACE"]
    call(chown_cmd)
    call(["mv", "/etc/sudoers.REPLACE", "/etc/sudoers.REPLACE"])

    def systemctlEnable(target):
        systemctl_cmd = ["systemctl", "enable", target]
        call(systemctl_cmd)

    systemctlEnable("network.service")
    systemctlEnable("sshd.service")
    systemctlEnable("nfsd.service")
    systemctlEnable("rpc-idmapd.service")
    systemctlEnable("ntpd.service")
