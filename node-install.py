#!/usr/bin/env python

import os
import configparser
from subprocess import call
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
    logger.debud(dd_cmd)
    #call(dd_cmd)
    logger.debug("Initializing new disk label")
    mklabel_cmd = ["parted", device, "mklabel", "gpt"]
    logger.debug(parted_cmd)
    #call(mklabel_cmd)
    for i,part in enumerate(partitions):
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
        logger.debug(parted_cmd)
        #call(parted_cmd)
        if option[2] not in ["ext2","ext3","ext4"]:
            continue
        logger.debug("Making FileSystem")
        mkfs_cmd = ["mkfs.%s" % option[2], device]
        #call(mkfs_cmd)

def mount_partitions():
    mounts = getKeys("FSTAB")
    rel_root = "/mnt"
    for mount in mounts:
        logger.debug("(Creating and) mounting %s" % mount)
        dev = getConfig("PARTITION_TABLE", mount)
        m = getConfig("FSTAB", mount)
        mkdir_cmd = ["mkdir", "-p", rel_root + m]
        mount_cmd = ["mount", dev, rel_root + m]
        logger.debug(mkdir_cmd)
        #call(mkdir_cmd)
        logger.debug(mount_cmd)
        #call(mount_cmd)
