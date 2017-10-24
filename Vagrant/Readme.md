# Vagrantfile for openvpn-config testing

### System configuration prerequisites

The VM uses NAT networking.

Port 1194 (host) is forwarded to port 1194 (guest), UDP. This enables OpenVPN
traffic to the network.

### System Package Prerequisites

Several package prerequisites (and their dependencies) are provisioned by this V
agrantfile:

 - python3-pip
 - openvpn
 - easy-rsa
 - pip (upgraded)
 - virtualenv (via pip)

### Python Package Prerequisites

See `../requirements.txt` for details.
