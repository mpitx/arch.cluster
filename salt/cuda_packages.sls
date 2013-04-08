cuda_packages:
    pkg.latest:
        - pkgs:
            - cuda
            - pycuda-headers
            - python-pycuda
            - python2-pycuda
    file.managed:
        - source: salt://root/load_cuda.sh
        - user: root
        - group: root
        - mode: 744

    file.managed:
        - source: salt//root/unload_cuda.sh
        - user: root
        - group: root
        - mode: 744
    file.managed:
        - source: salt//etc/systemd/system/multi-user.target.wants/cuda.service
        - user: root
        - group: root
        - mode: 777
