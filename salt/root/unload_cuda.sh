#!/bin/sh

if [ "$?" -eq 0 ]; then

    # Count the number of NVIDIA controllers found.
    N3D=`/usr/sbin/lspci | grep -i NVIDIA | grep "3D controller" | wc -l`
    NVGA=`/usr/sbin/lspci | grep -i NVIDIA | grep "VGA compatible controller" \
                          | wc -l`
    N=`expr $N3D + $NVGA - 1`
    for i in `seq 0 $N`; do
       rm -f /dev/nvidia$i
    done

    rm -f /dev/nvidiactl

else
    exit 1
fi
