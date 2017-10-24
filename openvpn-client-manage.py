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
from jinja2 import Template
import shutil
import os
import subprocess
import argparse

client_conf = {
    'public_server_address': '10.23.0.23',
    'public_server_port': '1192',
    'protocol': 'tcp'
}

ca_directory = '/etc/openvpn/openvpn-ca'
ca_keys_directory = '/etc/openvpn/openvpn-ca/keys'
openvpn_conf_directory = '/etc/openvpn'
working_dir = os.getcwd()
ovpn_template = os.path.join(working_dir, 'templates/client.conf.j2')


def file_from_template(template_file, output_file, vars_dict):
    '''
    Creates a file from the specified Jinja2 template
    '''

    with open(template_file) as template_file, \
            open(output_file, 'w') as output_file:

        template = Template(template_file.read())
        output_file.write(template.render(vars_dict))

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
        (key, _, value) = line.decode('ascii').rstrip().partition("=")
        os.environ[key] = value

    proc.communicate()


def create_client_keys(client):
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
    subprocess.call(['./pkitool', client])

    ca_cert = os.path.join(ca_keys_directory, 'ca.crt')
    client_cert = os.path.join(ca_keys_directory, client + '.crt')
    client_key = os.path.join(ca_keys_directory, client + '.key')
    ta_key = os.path.join(ca_keys_directory, 'ta.key')
    ovpn_output = os.path.join(working_dir, client + '.ovpn')

    # create .ovpn client file from template
    with open(ca_cert) as ca_cert_file, \
            open(client_cert) as client_cert_file, \
            open(client_key) as client_key_file, \
            open(ta_key) as ta_key_file:

        client_conf['ca_cert'] = ca_cert_file.read()
        client_conf['client_cert'] = client_cert_file.read()
        client_conf['client_key'] = client_key_file.read()
        client_conf['ta_key'] = ta_key_file.read()

        file_from_template(ovpn_template, ovpn_output, client_conf)


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
    print('running revoke-full in ' + ca_directory + ' to revoke client keys')
    subprocess.call(['./revoke-full', client])

    # copy crl file
    print('copying crl file')
    crl_file = os.path.join(ca_keys_directory, 'crl.pem')
    shutil.copy(crl_file, openvpn_conf_directory)

    # reload openvpn settings to pick up the changes
    print('restarting openvpn')
    subprocess.call(['systemctl', 'restart', 'openvpn@server'])


if __name__ == '__main__':
    # parse arguments
    argument_parser = argparse.ArgumentParser(description =
            'Create or revoke client keys, generating an .ovpn file if needed.')

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
