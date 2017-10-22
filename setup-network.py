#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Inspired by: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-16-04

This will do the following:

 - set up port forwarding via `echo 1 > /proc/sys/net/ipv4/ip_forward`
 - sets up masquerading via `iptables -t nat -A POSTROUTING ! -d 10.8.0.0/8 -j MASQUERADE`
 - sets up a forwarding rule via `iptables -A FORWARD -j ACCEPT`
 - start the openvpn server (?)
'''

import subprocess

if __name__ == '__main__':

    # echo 1 > /proc/sys/net/ipv4/ip_forward
    with open("/proc/sys/net/ipv4/ip_forward", 'w') as ipfwd:
        ipfwd.write("1")

    # Enable masquerading
    subprocess.call(['iptables', '-t', 'nat', '-A', 'POSTROUTING', '!', '-d',
                         '10.8.0.0/8', '-j', 'MASQUERADE'])

    # Enable forwarding
    subprocess.call(['iptables', '-A', 'FOWRARD', '-j', 'ACCEPT'])
