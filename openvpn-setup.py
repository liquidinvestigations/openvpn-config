#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Inspired by: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-16-04

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

Requires root to run.
'''

from jinja2 import Template
import os
import subprocess
import sys
import shutil

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

default_server_conf = {
    'port': '1192',
    'protocol': 'tcp'
}

# set up some paths
# templates
template_dir = os.path.join(os.getcwd(),'templates')
vars_template_file = os.path.join(template_dir, 'vars.j2')
conf_template_file = os.path.join(template_dir, 'server.conf.j2')

# certificate authority
ca_output_dir = '/etc/openvpn/openvpn-ca'
vars_output_file = os.path.join(ca_output_dir,'vars')

# keys
ca_keys_dir = '/etc/openvpn/openvpn-ca/keys'
keyfiles = list(map(lambda x: os.path.join(ca_keys_dir, x),
               ['ca.crt', 'ca.key', 'server.crt', 'server.key', 'ta.key', 'dh2048.pem']))

# configuration
conf_output_dir = '/etc/openvpn'
conf_output_file = os.path.join(conf_output_dir, 'server.conf')

def file_from_template(template_file, output_file, vars_dict):
    '''
    Creates a file from the specified Jinja2 template
    '''
    with open(template_file) as template_file, \
            open(output_file, 'w') as output_file:

        template = Template(template_file.read())
        output_file.write(template.render(vars_dict))

if __name__ == '__main__':
    ''' note: this expects that ca_output_dir doesn't exist
    '''
    # Set up CA directory
    print("setting up certificate authority directory")
    subprocess.call(['make-cadir', ca_output_dir])

    # Create 'vars' file from template
    print("creating vars file from template")
    file_from_template(vars_template_file, vars_output_file, default_ca_vars)

    # 'source' the vars file.
    # this creates a bash subprocess, sources the file, outputs the new
    # environment, then writes it to os.environ, key by key.
    # TODO: proper error handling here on Popen() and communicate()
    print("setting OS environment from vars file")
    os.chdir(ca_output_dir)
    command = ['bash', '-c', 'source ' + vars_output_file + ' && env']

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

    print('cleaning up before key generation (running ./clean-all)')
    subprocess.call(['./clean-all'])

    print('running pkitool to initialize ca')
    subprocess.call(['./pkitool', '--initca'])

    print('running pkitool to initialize server certs')
    subprocess.call(['./pkitool', '--server', 'server'])

    print('running openssl to generate strong Diffie-Hellman keys')
    # NOTE: i've added the '-dsaparam' option here. research says that it's
    #       practically just as strong, but generates *much* faster.
    #       see : https://security.stackexchange.com/a/95184
    #       i can't find another reference to this, so if anyone wants to
    #       do the research to tell me why this is terrible, i'd love to hear it
    subprocess.call(['openssl', 'dhparam', '-dsaparam', '-out', dh_file, key_size])

    print('generating OpenVPN HMAC signature')
    subprocess.call(['openvpn', '--genkey', '--secret', hmac_file])

    print('generating server.conf')
    file_from_template(conf_template_file, conf_output_file, default_server_conf)

    print('copying keys and certs to /etc/openvpn')
    for keyfile in keyfiles:
        shutil.copy2(keyfile, conf_output_dir)

    print('initializing revocation list')
    subprocess.call(['./pkitool', 'CRL_INIT'])
    subprocess.call(['./revoke-full', 'CRL_INIT'])
    revocation_list = os.path.join(ca_keys_dir, 'crl.pem')
    shutil.copy2(revocation_list, conf_output_dir)

    print('turning on ip forwarding')
    with open("/proc/sys/net/ipv4/ip_forward", 'w') as ipfwd:
        ipfwd.write("1")

    print('enabling masquerading')
    subprocess.call(['iptables', '-t', 'nat', '-A', 'POSTROUTING', '!', '-d',
                         '10.8.0.0/8', '-j', 'MASQUERADE'])

    print('enabling forwarding')
    subprocess.call(['iptables', '-A', 'FORWARD', '-j', 'ACCEPT'])

    print('starting openvpn')
    subprocess.call(['systemctl', 'start', 'openvpn@server'])
