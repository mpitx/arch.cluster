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

/etc/resolv.conf:
    file.managed:
        - source: salt://etc/resolv.conf
        - user: root
        - group: root
        - mode: 644

/etc/locale.gen:
    file.managed:
        - source: salt://etc/locale.gen
        - user: root
        - group: root
        - mode: 644

/etc/profile:
    file.managed:
        - source: salt://etc/profile
        - user: root
        - group: root
        - mode: 644
