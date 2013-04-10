base:
    '*':
        - base_packages
        - users
        - fstab
    'os:Arch':
        - match: grain
        - arch
    'cuda':
        - match: nodegroup
        - cuda_packages
        - mpi_packages
    'desktop':
        - match: nodegroup
        - desktop_packages
