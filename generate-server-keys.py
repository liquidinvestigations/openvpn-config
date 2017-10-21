#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Inspired by: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-16-04
'''

from jinja2 import Template
import os
import subprocess
import sys

# Default settings for CA template
default_ca_vars = {
    'key_country': '"US"',
    'key_province': '"MI"',
    'key_city': '"Detroit"',
    'key_org': '"LiquidInvestigations"',
    'key_email': '"support@liquiddemo.org"',
    'key_ou': '"node"',
    'key_name': '"detroit-liquid.local"'
}

# set up some paths
ca_template_dir = os.path.join(os.getcwd(),'templates')
ca_template_file = 'vars.j2'
ca_output_dir = os.path.join(os.getcwd(),'openvpn-ca')
ca_output_file = 'vars'

def create_ca_vars(input_template_file, output_file, vars_dict):
    '''
    Creates an easy-rsa vars file from the supplied template and
    dictionary. Output file is specified as output_file.
    '''
    with open(input_template_file) as vars_template, \
            open(output_file, 'w') as vars_output:

        vars_template = Template(vars_template.read())
        vars_output.write(vars_template.render(vars_dict))

if __name__ == '__main__':
    ''' note: this expects that ca_output_dir doesn't exist
    '''
    # Set up CA directory
    print("setting up certificate authority directory")
    subprocess.call(['make-cadir', ca_output_dir])

    template_file = os.path.join(ca_template_dir, ca_template_file)
    output_file = os.path.join(ca_output_dir, ca_output_file)

    # Create 'vars' file from template
    print("creating vars file from template")
    create_ca_vars(template_file, output_file, default_ca_vars)

    # 'source' the vars file.
    # this creates a bash subprocess, sources the file, outputs the new
    # environment, then writes it to os.environ, key by key.
    # TODO: proper error handling here on Popen() and communicate()
    print("setting OS environment from vars file")
    os.chdir(ca_output_dir)
    command = ['bash', '-c', 'source ' + output_file + ' && env']

    proc = subprocess.Popen(command, stdout = subprocess.PIPE)

    for line in proc.stdout:
        # TODO: are we OK to just 'decode('ascii').rstrip() here?'
        (key, _, value) = line.decode('ascii').rstrip().partition("=")
        os.environ[key] = value

    proc.communicate()

    # clean the keys directory, generate certificates and keys
    os.chdir(ca_output_dir)
    key_dir = os.environ['KEY_DIR']
    key_size = os.environ['KEY_SIZE']
    dh_file = os.path.join(key_dir, 'dh' + key_size + '.pem')
    hmac_file = os.path.join(key_dir, 'ta.key')

    print('')
    print('cleaning up before key generation (running ./clean-all)')
    subprocess.call(['./clean-all'])

    print('running pkitool to initialize ca')
    subprocess.call(['./pkitool', '--initca'])

    print('running pkitool to initialize server certs')
    subprocess.call(['./pkitool', '--server', 'server'])

    print('running openssl to generate strong Diffie-Hellman keys')
    subprocess.call(['openssl', 'dhparam', '-out', 'dh_file', key_size])

    print('generating OpenVPN HMAC signature')
    subprocess.call(['openvpn', '--genkey', '--secret', hmac_file])
