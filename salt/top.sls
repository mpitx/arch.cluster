base:
    '*':
        - base_packages
        - users
        - fstab
    'os:Arch':
        - match: grain
        - arch
