/etc/mkinitcpio.conf:
    file.managed:
        - source: salt://etc/mkinitcpio.conf
        - user: root
        - group: root
        - mode: 644

/etc/pacman.conf:
    file.managed:
        - source: salt://etc/pacman.conf
        - user: root
        - group: root
        - mode: 644

/etc/pacman.d/mirrorlist:
    file.managed:
        - source: salt://etc/pacman_mirrorlist
        - user: root
        - group: root
        - mode: 644
