# Arch Cluster #

Arch Cluster Build/Configuration Information

## Notes ##

There are some hard coded assumptions that are in the process of being massaged
out.

## Install Steps (Node) ##

1.  Boot Latest Arch Media [Arch Linux Downloads][archDownload]

2.  Setup Network Connections:

    This is (/ should be) done for you

    However, if you require static IP see
    [configuring network][archConfigNetwork]

3.  Install Git:

        pacman -Sy git

    Something to note here, you may not want to upgrade pacman first. This
    is just unnecessary here; this is a live cd.

4.  Clone [this] repository

5.  `cd` into cloned directory

6.  Make any modifications needed for configuration (config.sh)

7.  Execute `node-install.sh {node_number}`

8.  Reboot into new system

9.  Ensure `salt` is setup correctly:

    Add the new node's key on the master node

    Allow salt to configure the box (master node salt states are in progress)

    Reboot

    (For more information about salt, visit [saltstack].)

## License ##

*arch.cluster* is available under the GNU General Public License (version 3).
For more information see the LICENSE text file.

[archConfigNetwork]:https://wiki.archlinux.org/index.php/Configuring_network
[this]:https://github.com/mpitx/arch.cluster.git
[saltstack]:http://docs.saltstack.org/
[archDownload]:https://www.archlinux.org/download/
