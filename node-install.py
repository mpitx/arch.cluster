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
    #call(["dd", "if=/dev/zero", "of=%s" % device, "bs=512", "count=1"])
    logger.debug("Initializing new disk label")
    #call(["parted", device, "mklabel", "gpt"])
    for i,part in enumerate(partitions):
        logger.debug("Creating %d partition" % i)
        options = part.split(";")
        assert 3 <= len(options) <= 3 ##this may later grow
        #call(["parted",
        #     device,
        #     "mkpart",
        #     "P1",
        #     options[2],
        #     options[1],
        #     options[2]])
        if option[2] not in ["ext2","ext3","ext4"]:
            continue
        logger.debug("Making FileSystem")
        #call(["mkfs.%s" % option[2], device])

def mount_partitions():
    mounts = getKeys("FSTAB")
    rel_root = "/mnt"
    for mount in mounts:
        logger.debug("(Creating and) mounting %s" % mount)
        dev = getConfig("PARTITION_TABLE", mount)
        m = getConfig("FSTAB", mount)
        #call(["mkdir", "-p", rel_root + m])
        #call(["mount", dev, rel_root + m])
