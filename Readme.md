# Liquid Investigations: OpenVPN Configuration PoC

This repository houses some python scripts to configure OpenVPN. This is to be
integrated with the setup repository, but serves for now as a PoC. It is
inspired by [this](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-16-04)
tutorial. Revoking certificates is discussed [here](https://blog.remibergsma.com/2013/02/27/improving-openvpn-security-by-revoking-unneeded-certificates/).

To play with this setup, run `vagrant up` in the `Vagrant/` folder.

TODO: more experimentation needs to be done to ensure that this configuration
template supports discovery (zeroconf).

### Prerequisites

The `Vagrantfile` takes care of all the setup, and installs the following
prerequisites (see `./Vagrant/Readme.md` for details).:

 - Ubuntu 16.10
 - python3-pip
 - OpenVPN
 - easy-rsa
 - virtualenv

It then creates a virtualenv, and installs Python dependencies from
`requirements.txt`

### Scripts

`./create-client-ovpn.py`:

Requires root to run.

 - Creates a CA in /etc/openvpn/openvpn-ca
 - Creates a CA config (vars) from template
 - Installs certs and key database in /etc/openvpn/openvpn-ca/keys.
 - Creates a server.conf from template, installs in /etc/openvpn
 - Installs certificates and keys in /etc/openvpn
 - Configures the network:
    - sets up port forwarding via `echo 1 > /proc/sys/net/ipv4/ip_forward`
    - sets up masquerading via `iptables -t nat -A POSTROUTING ! -d 10.8.0.0/8 -j MASQUERADE`
    - sets up a forwarding rule via `iptables -A FORWARD -j ACCEPT`
 - Starts OpenVPN


TODO : `./ovpn-client.py`:

This script manages keys and .ovpn files for OpenVPN users.
