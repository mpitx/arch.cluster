#!/usr/bin/env python

import os
import configparser
import subprocess
import sys
import logging

logger = logging.getLogger("install")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def getConfig(section, key):
    config = configparser.ConfigParser()
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
        sub = subprocess.Popen(cmd, stdout=stdout, stderr=stderr,
                               stdin=subprocess.PIPE if input else None)
        sub.communicate(input=input)

def prepare_disks():
    ROOT = getConfig("DISK_INFO", "ROOT")
    DEVICES = getKeys("PARTITION_TABLE")
    for device in DEVICES:
        partitionDisk(device)

def partitionDisk(device):
    logger.debug("Partitioning %s" % device)
    partitionTable = getConfig("PARTITION_TABLE", device)
    partitions = partitionTable.split('|')
    logger.debug("Erasing current partition table")
    call(["dd", "if=/dev/zero", "of=%s" %device, "bs=512", "cound=1"])
    logger.debug("Initializing new disk label")
    call(["parted", device, "mklabel", "gpt"])
    for i, part in enumerate(partitions):
        logger.debug("Creating %d partition" % i)
        options = part.split(";")
        assert 3 <= len(options) <= 3 ##this may later grow
        call(["parted",
                      device,
                      "mkpart",
                      "P1",
                      options[2],
                      options[1],
                      options[2]])
        if options[2] not in ["ext2", "ext3", "ext4"]:
            continue
        logger.debug("Making FileSystem")
        call(["mkfs.%s" % options[2], device])

def mount_partitions():
    mounts = getKeys("FSTAB")
    rel_root = "/mnt"
    for mount in mounts:
        logger.debug("(Creating and) mounting %s" % mount)
        dev = getConfig("PARTITION_TABLE", mount)
        m = getConfig("FSTAB", mount)
        call(["mkdir", "-p", rel_root + m])
        call(["mount", dev, rel_root + m])

def umount_partitions():
    mounts = getKeys("FSTAB")
    mounts.reverse()
    rel_root = "/mnt"
    for mount in mounts:
        logger.debug("Unmount %s" % mount)
        m = getConfig("FSTAB", mount)
        call(["umount", m])

def bootstrap_system():
    call(["pacstrap", "/mnt", "base", "base-devel"])
    call(["rsync", "-avz", "mntfiles", "/mnt/"])
    genfstab_cmd = ["genfstab", "-U", "-p", "/mnt"]
    with open("/mnt/etc/fstab", "a") as fstab:
        call(genfstab_cmd, stdout=fstab)

def live_install_main():
    prepare_disks()
    mount_partitions()
    bootstrap_system()
    logger.debug("Copy and call self from chroot")
    call(["cp", os.path.join(os.getcwd(), "node-install.py"),
                     "/mnt/root/node-enstall.py"])
    call(["arch-chroot",
                  "/mnt",
                  "python",
                  "node-install.py",
                  "node-number",
                  "in-chroot"])
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

    call(["pacman",
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
          "rsync"])
    call(["locale-gen"])

    call(["ln", "-s",
          "/usr/share/zoneinfo/%s" % zoneInfo,
          "/etc/localtime"])

    call(["hwclock", "--systohc", "--utc"])

    hostname_cmd = ["echo", hostname]
    logger.debug("%s piped to /etc/hostname" % hostname_cmd)
    with open("/etc/hostname", "w") as f:
        call(hostname_cmd, stdout=f)

    call(["mkinitcpio", "-p", "linux"])

    call(["chpasswd"], input="root:toor")

    call(["mv", "/boot/syslinux/syslinux.cfg.REPLACE",
          "/boot/syslinux/syslinux.cfg"])

    call(["syslinux-install_update", "-iam"])

    os.mkdir("/etc/conf.d")
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
    export = getConfig("NFS_SHARE", "SERVER_EXPORT")
    mount_point = getConfig("NFS_SHARE", "MOUNT_POINT")
    mount_options = getConfig("NFS_SHARE", "OPTIONS")
    mount_dump = getConfig("NFS_SHARE", "DUMP")
    mount_fsckorder = getConfig("NFS_SHARE", "FSCKORDER")
    call(["mv", "/etc/idmapd.conf.REPLACE", "/etc/idmapd.conf"])
    with open("/etc/fstab", "a") as fstab:
        fstab.write("""
            #NFSv4 home mount
            %s %s nfs4 %s %s %s"""
            % (export,
               mount_point,
               mount_options,
               mount_dump,
               mount_fsckorder))

    call(["chown", "root:root", "/etc/sudoers.REPLACE"])
    call(["mv", "/etc/sudoers.REPLACE", "/etc/sudoers.REPLACE"])

    def systemctlEnable(target):
        systemctl_cmd = ["systemctl", "enable", target]
        call(systemctl_cmd)

    systemctlEnable("network.service")
    systemctlEnable("sshd.service")
    systemctlEnable("nfsd.service")
    systemctlEnable("rpc-idmapd.service")
    systemctlEnable("ntpd.service")

def full_install():
    prepare_disks()
    mount_partitions()
    bootstrap_system()
    live_install_main()
    umount_partitions()

if __name__ == '__main__':
    assert len(sys.argv) == 2
    if sys.argv[1] == "full-install":
        full_install()
    elif sys.argv[1] == "in-chroot":
        chroot_stage_main()
    else:
        sys.exit(1)
