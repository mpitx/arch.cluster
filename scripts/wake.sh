#!/usr/bin/env sh

# Foreach line in STDIN, attempt to wake up a node
# LINE syntax is as follows:
# <node/hostname> <IP-address> <MAC Address>
# Hostname: this is simply for identification purposes
# IP-Address: make `wol` select the right interface
# MAC Address: required for actually sending the `wol` packet

while read LINE
do
    ipaddr=`echo ${LINE} | awk '{print $2}'`
    macaddr=`echo ${LINE} | awk '{print $3}'`
    wol --ipaddr=${ipaddr} ${macaddr}
done
