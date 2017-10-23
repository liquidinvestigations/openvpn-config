#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Inspired by: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-16-04
Inspired by: https://blog.remibergsma.com/2013/02/27/improving-openvpn-security-by-revoking-unneeded-certificates/

This script will:

 - generate and register client keys
 - generate a client .ovpn file for installation

OR

 - revoke client keys
 - reload the revoked certificates list in openvpn-ca

This script expects an installed Certificate Authority. It will default to one
in `/etc/openvpn/openvpn-ca`.

This script should be run with root priveleges, as it needs access to the CA in
`/etc/openvpn/openvpn-ca`

'''

import os
import subprocess
import argparse

ca_directory = '/etc/openvpn/openvpn-ca'

def source_CA_vars():
    '''
    'source' the CA vars file.
    this creates a bash subprocess, sources the file, outputs the new
    environment, then writes it to os.environ, key by key.
    TODO: proper error handling here on Popen() and communicate()
    '''
    print("setting OS environment from vars file")
    os.chdir(ca_directory)
    command = ['bash', '-c', 'source ' + 'vars' + ' && env']

    proc = subprocess.Popen(command, stdout = subprocess.PIPE)

    for line in proc.stdout:
        # TODO: are we OK to just 'decode('ascii').rstrip() here?'
        (key, _, value) = line.decode('ascii').rstrip().partition("=")
        os.environ[key] = value

    proc.communicate()

def create_client_keys(client, ovpn_output_file):
    '''
    Creates client keys for the specified `client`. Creates the specified .ovpn
    config file.
    '''

    # source vars for interacting with CA
    source_CA_vars()
    # enter the CA directory
    os.chdir(ca_directory)

    # run pkitool, create keys
    print('running pkitool in ' + ca_directory + ' to create client keys')
    # subprocess.call(['./pkitool', client])
    # create .ovpn client file from template

    pass

def revoke_client_keys(client):
    '''
    Revokes client keys for the specified `client`. Updates the revoked keys
    database and reloads the openvpn configuration.
    TODO: does reloading the config drop all existing connections?
    '''

    # source vars for interacting with CA
    source_CA_vars()
    # enter the CA directory
    os.chdir(ca_directory)

    # revoke keys
    print('running revoke-all in ' + ca_directory + ' to revoke client keys')
    # copy revoked key database
    # reload openvpn settings to pick up the changes

    pass

if __name__ == '__main__':
    # parse arguments
    argument_parser = argparse.ArgumentParser(description =
            'Create or revoke client keys, generating an .ovpn file as needed.')

    group = argument_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--create', action='store_true', help='Create client keys.')
    group.add_argument('-r', '--revoke', action='store_true', help='Revoke client keys.')

    argument_parser.add_argument('client', help='The name for the client.')
    args = argument_parser.parse_args()
    create = args.create
    revoke = args.revoke
    client = args.client

    if (create):
        print('creating client keys')
        create_client_keys(client)

    if (revoke):
        print('revoking client keys')
        revoke_client_keys(client)
