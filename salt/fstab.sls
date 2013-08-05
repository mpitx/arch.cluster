/etc/fstab:
    file.append:
        - text: |
            # NFS mounts
            192.168.1.254:/home         /home                       nfs4 soft,cto,rw,suid,noatime,exec,rsize=8192,wsize=8192,timeo=20  0 0
            192.168.1.254:/pacmanCache  /var/cache/pacman/shared    nfs4    soft,rw,noatime,rsize=8192,wsize=8192,timeo=20  0 0
