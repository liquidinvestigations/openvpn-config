#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Inspired by: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-16-04

This will do the following:

 - set up port forwarding via `echo 1 > /proc/sys/net/ipv4/ip_forward`
 - sets up masquerading via `iptables -t nat -A POSTROUTING ! -d 10.8.0.0/8 -j MASQUERADE`
 - sets up a forwarding rule via `iptables -A FORWARD -j ACCEPT` TODO: this is
   probably too permissive or wrong.
 - start the openvpn server (?)
```
