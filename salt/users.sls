{# NOTE: could specify actual usernames here, but this is simpler for now #}

/etc/passwd:
    file.managed:
        - source: salt://etc/passwd
        - user: root
        - group: root
        - mode: 644

/etc/group:
    file.managed:
        - source: salt://etc/group
        - user: root
        - group: root
        - mode: 644

/etc/shadow:
    file.managed:
        - source: salt://etc/shadow
        - user: root
        - group: root
        - mode: 600

/etc/gshadow:
    file.managed:
        - source: salt://etc/gshadow
        - user: root
        - group: root
        - mode: 600

