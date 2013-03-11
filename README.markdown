# Arch Cluster #

Arch Cluster Build/Configuration Information

## Notes ##

There are some hard coded assumptions that are in the process of being massaged
out.

## Install Steps (Node) Draft ##

1.  Boot Latest Arch Media

2.  Setup Network Connections

    *   This is done for you

    *   However, if you require static IP see
        [configuring network][archConfigNetwork]

3.  Install Git

    *   `pacman -S git`

4.  Clone [this] repository

5.  `cd` into cloned directory

6.  Make any modifications needed for configuration (config.sh)

7.  Execute `node-install.sh {node_number}`

8.  Reboot into new system

9.  Ensure `salt` is setup correctly

    *   Add the new node's key on the master node

    *   Allow salt to configure the box

    *   Reboot

[archConfigNetwork]:[https://wiki.archlinux.org/index.php/Configuring_network]
[this]:[https://github.com/mpitx/arch.cluster.git]
